import { createInterface } from 'node:readline/promises';
import { stdin, stdout } from 'node:process';
import type { Session, SessionOutcome, Quote } from '../types.js';
import { streamQuestion, getConversationModel, getModelForFile } from '../llm/client.js';
import { getSystemPrompt } from '../llm/prompts.js';
import { validateResponse, repromptIfInvalid, getFallbackQuestion } from '../llm/validator.js';
import { detectFilePaths, readCodeFile, formatCodeContext } from '../storage/file-reader.js';
import { addTurn, addCodeFile } from './session.js';
import { checkAndSummarize, buildMessageArray, estimateTokens } from './context-manager.js';
import { selectQuote } from '../quotes/selector.js';
import {
  streamToTerminal,
  newLine,
  displaySessionHeader,
  displayDim,
} from '../ui/renderer.js';

const EXIT_COMMANDS = new Set(['exit', 'quit']);
const SOLVE_COMMANDS = new Set(['solved', 'found it']);

export interface SessionLoopResult {
  outcome: SessionOutcome;
}

export async function runSessionLoop(session: Session): Promise<SessionLoopResult> {
  const rl = createInterface({ input: stdin, output: stdout });
  const codeFiles = new Map<string, string>();
  let rollingSummary: string | undefined;
  let lifelineOffered = false;

  displaySessionHeader(session.intensity);

  // Read initial code files from problem description
  const initialPaths = detectFilePaths(session.problemDescription);
  for (const filePath of initialPaths) {
    const content = await readCodeFile(filePath);
    if (content) {
      codeFiles.set(filePath, content);
      addCodeFile(session, filePath);
    }
  }

  // Generate opening question
  let model = initialPaths.length > 0 ? getModelForFile(initialPaths[0]) : getConversationModel();
  const codeContext = formatCodeContext(codeFiles);
  let systemPrompt = getSystemPrompt(
    session.intensity,
    session.problemDescription,
    codeContext || undefined,
    rollingSummary,
    1,
  );

  const openingQuestion = await generateValidQuestion(
    systemPrompt,
    [{ role: 'user', content: session.problemDescription }],
    model,
    session.intensity,
  );

  newLine();
  displayDim(`[Turn 1]`);
  console.log(openingQuestion);
  newLine();

  // Add opening turn with empty response (to be filled when user responds)
  let currentQuestion = openingQuestion;

  try {
    while (true) {
      const input = await rl.question('> ');
      const trimmed = input.trim();

      if (!trimmed) continue;

      const lower = trimmed.toLowerCase();

      // Check exit commands
      if (EXIT_COMMANDS.has(lower)) {
        addTurn(session, currentQuestion, '[exited]', model);
        rl.close();
        return { outcome: 'abandoned' };
      }

      // Check solve commands
      if (SOLVE_COMMANDS.has(lower)) {
        addTurn(session, currentQuestion, '[solved]', model);
        rl.close();
        return { outcome: 'solved' };
      }

      // Check "I give up"
      if (lower === 'i give up') {
        if (!lifelineOffered) {
          lifelineOffered = true;
          addTurn(session, currentQuestion, trimmed, model);

          // Generate one lifeline question
          const lifelinePrompt = getSystemPrompt(
            session.intensity,
            session.problemDescription,
            codeContext || undefined,
            rollingSummary,
            session.transcript.length + 1,
          );
          const messages = buildConversationMessages(session, trimmed);
          const lifelineQ = await generateValidQuestion(
            lifelinePrompt,
            [...messages, { role: 'user', content: 'I give up. I cannot figure this out.' }],
            getConversationModel(),
            session.intensity,
          );

          newLine();
          displayDim(`[Lifeline — one more question before you go]`);
          console.log(lifelineQ);
          newLine();
          currentQuestion = lifelineQ;
          continue;
        } else {
          addTurn(session, currentQuestion, '[gave up]', model);
          rl.close();
          return { outcome: 'abandoned' };
        }
      }

      // Normal response — process it
      addTurn(session, currentQuestion, trimmed, model);

      // Check for new file paths in response
      const newPaths = detectFilePaths(trimmed);
      for (const filePath of newPaths) {
        if (!codeFiles.has(filePath)) {
          const content = await readCodeFile(filePath);
          if (content) {
            codeFiles.set(filePath, content);
            addCodeFile(session, filePath);
          }
        }
      }

      // Check context window
      const contextResult = await checkAndSummarize(
        systemPrompt,
        session.transcript,
        rollingSummary,
      );
      rollingSummary = contextResult.summary;

      // Select contextual quote
      const quote = selectQuote(trimmed);
      const suggestedQuoteText = quote ? quote.text : undefined;

      // Build next turn
      const turnNumber = session.transcript.length + 1;
      const updatedCodeContext = formatCodeContext(codeFiles);
      systemPrompt = getSystemPrompt(
        session.intensity,
        session.problemDescription,
        updatedCodeContext || undefined,
        rollingSummary,
        turnNumber,
        suggestedQuoteText,
      );

      // Determine model — Sonnet for first analysis of new files
      model = newPaths.length > 0 ? getModelForFile(newPaths[0]) : getConversationModel();

      const messages = buildConversationMessages(session);
      const nextQuestion = await generateValidQuestion(
        systemPrompt,
        messages,
        model,
        session.intensity,
      );

      newLine();
      displayDim(`[Turn ${turnNumber}]`);
      console.log(nextQuestion);
      newLine();
      currentQuestion = nextQuestion;
    }
  } catch (error) {
    // Handle Ctrl+C / Ctrl+D / readline close
    if ((error as NodeJS.ErrnoException).code === 'ERR_USE_AFTER_CLOSE') {
      return { outcome: 'abandoned' };
    }
    rl.close();
    return { outcome: 'abandoned' };
  }
}

async function generateValidQuestion(
  systemPrompt: string,
  messages: Array<{ role: 'user' | 'assistant'; content: string }>,
  model: string,
  intensity: Session['intensity'],
): Promise<string> {
  let fullText = '';

  await streamQuestion(systemPrompt, messages, model, {
    onText: (text) => streamToTerminal(text),
    onComplete: (text) => {
      fullText = text;
    },
    onError: () => {},
  });

  // Clear the streamed output line
  process.stdout.write('\r\x1b[K');

  const validation = validateResponse(fullText);
  if (validation.valid) return fullText;

  // Try reprompt
  const reprompted = await repromptIfInvalid(systemPrompt, messages, fullText);
  if (reprompted) return reprompted;

  // Fallback
  return getFallbackQuestion(intensity);
}

function buildConversationMessages(
  session: Session,
  currentResponse?: string,
): Array<{ role: 'user' | 'assistant'; content: string }> {
  const messages: Array<{ role: 'user' | 'assistant'; content: string }> = [
    { role: 'user', content: session.problemDescription },
  ];

  for (const turn of session.transcript) {
    messages.push({ role: 'assistant', content: turn.question });
    if (turn.response && !turn.response.startsWith('[')) {
      messages.push({ role: 'user', content: turn.response });
    }
  }

  if (currentResponse) {
    messages.push({ role: 'user', content: currentResponse });
  }

  return messages;
}
