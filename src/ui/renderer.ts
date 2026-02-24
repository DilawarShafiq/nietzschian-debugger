const RESET = '\x1b[0m';
const BOLD = '\x1b[1m';
const DIM = '\x1b[2m';
const YELLOW = '\x1b[33m';
const RED = '\x1b[31m';
const GREEN = '\x1b[32m';
const CYAN = '\x1b[36m';

export function streamToTerminal(text: string): void {
  process.stdout.write(text);
}

export function newLine(): void {
  process.stdout.write('\n');
}

export function displayMessage(message: string): void {
  console.log(message);
}

export function displayBold(message: string): void {
  console.log(`${BOLD}${message}${RESET}`);
}

export function displayDim(message: string): void {
  console.log(`${DIM}${message}${RESET}`);
}

export function displayError(message: string): void {
  console.error(`${RED}${BOLD}Error:${RESET} ${RED}${message}${RESET}`);
}

export function displayWarning(message: string): void {
  console.warn(`${YELLOW}${message}${RESET}`);
}

export function displaySuccess(message: string): void {
  console.log(`${GREEN}${message}${RESET}`);
}

export function displayQuote(text: string, philosopher: string): void {
  console.log(`\n${DIM}"${text}"${RESET}`);
  console.log(`${DIM} — ${philosopher}${RESET}`);
}

export function displaySessionHeader(intensity: string): void {
  const label = intensity.charAt(0).toUpperCase() + intensity.slice(1);
  console.log(`\n${BOLD}${CYAN}Nietzschian Debugger${RESET} ${DIM}[${label} mode]${RESET}\n`);
}

export function displayPrompt(): void {
  process.stdout.write(`${BOLD}> ${RESET}`);
}

export function displayApiKeyHelp(): void {
  console.log(`
${BOLD}${RED}Missing API Key${RESET}

Set your Anthropic API key to use the Nietzschian Debugger:

  ${BOLD}export ANTHROPIC_API_KEY=your-key-here${RESET}

Get a key at: ${CYAN}https://console.anthropic.com/${RESET}
`);
}
