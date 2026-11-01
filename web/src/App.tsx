import { useEffect, useRef, useState } from "react";
import {
  estimateInputTokens, systemPrompt,
  providerNames, type Provider,
  type ChatMessage, type Language, type Philosopher, type TokenUsage,
} from "../shared/prompts.js";
import { browserChat, browserChatError } from "../shared/browser-chat.js";
import { DEFAULT_MODELS, PROVIDER_ENDPOINTS } from "../shared/providers.js";
import { backendChat, backendOrigin, BackendChatError } from "../shared/backend-chat.js";
import { errors, partners, translations } from "./i18n.js";
import { demoQuestions, demoReply, initialDemoTopics, type DemoTopic } from "../shared/demo.js";
import { MessageContent } from "./MessageContent.js";

type DisplayMessage = ChatMessage & { philosopher?: Philosopher; safety?: boolean; demo?: boolean };
const avatarUrl = `${import.meta.env.BASE_URL}philosophers.png`;
const initialUsage: TokenUsage = { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 };
const configuredBackend = import.meta.env.VITE_API_BASE_URL
  ? backendOrigin(import.meta.env.VITE_API_BASE_URL) : "";

function Avatar({ philosopher, large = false }: { philosopher: Philosopher; large?: boolean }) {
  return <span
    className={`avatar ${large ? "avatar-large" : ""}`}
    role="img"
    aria-label={partners[philosopher].name}
    style={{
      backgroundImage: `url("${philosopher === "popper" ? `${import.meta.env.BASE_URL}popper.svg` : avatarUrl}")`,
      backgroundSize: philosopher === "popper" ? "cover" : "300% auto",
      backgroundPosition: `${partners[philosopher].position} 30%`,
    }}
  />;
}

export function App() {
  const [language, setLanguage] = useState<Language>("nl");
  const [philosopher, setPhilosopher] = useState<Philosopher>("nietzsche");
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [provider, setProvider] = useState<Provider>("claude");
  const [greenptRoute, setGreenptRoute] = useState<"direct" | "backend">(configuredBackend ? "backend" : "direct");
  const [backendToken, setBackendToken] = useState("");
  const [consent, setConsent] = useState(false);
  const [engine, setEngine] = useState<"demo" | "live">("demo");
  const [demoTopics, setDemoTopics] = useState<DemoTopic[]>(initialDemoTopics);
  const [demoTurns, setDemoTurns] = useState(0);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [requests, setRequests] = useState(0);
  const [providerRequests, setProviderRequests] = useState(0);
  const [usage, setUsage] = useState<TokenUsage>(initialUsage);
  const [model, setModel] = useState(DEFAULT_MODELS.claude);
  const [showPrompt, setShowPrompt] = useState(false);
  const dialog = useRef<HTMLDialogElement>(null);
  const lastMessage = useRef<HTMLDivElement>(null);
  const composer = useRef<HTMLTextAreaElement>(null);
  const locked = useRef(false);
  const t = translations[language];
  const partner = partners[philosopher];
  const viaBackend = provider === "greenpt" && greenptRoute === "backend";
  const nextMessages: ChatMessage[] = [
    ...messages.map(({ role, content }) => ({ role, content })),
    ...(draft.trim() ? [{ role: "user" as const, content: draft.trim() }] : []),
  ];
  const estimate = estimateInputTokens(language, philosopher, nextMessages);
  const format = (number: number) => number.toLocaleString(language === "nl" ? "nl-NL" : "en-GB");

  useEffect(() => {
    document.documentElement.lang = language;
    document.title = translations[language].title;
  }, [language]);
  useEffect(() => { lastMessage.current?.scrollIntoView({ behavior: "smooth", block: "end" }); }, [messages, pending]);
  useEffect(() => {
    if (showPrompt) dialog.current?.showModal();
    else dialog.current?.close();
  }, [showPrompt]);

  function addUsage(value?: TokenUsage, calls = 0) {
    if (value) {
      setUsage((previous) => ({
        input: previous.input + value.input, output: previous.output + value.output,
        cacheRead: previous.cacheRead + value.cacheRead, cacheWrite: previous.cacheWrite + value.cacheWrite,
      }));
    }
    setProviderRequests((previous) => previous + calls);
  }

  async function send(topic?: DemoTopic) {
    const submitted = topic ? demoQuestions[topic].label[language] : draft.trim();
    if (locked.current || (engine === "live" && !consent) || !submitted) return;
    const submittedMessages: ChatMessage[] = [
      ...messages.map(({ role, content }) => ({ role, content })),
      { role: "user", content: submitted },
    ];
    if (submittedMessages.length > 31 || submittedMessages.reduce((sum, message) => sum + message.content.length, 0) > 24000) {
      setError(t.limit); return;
    }
    if (engine === "demo") {
      setError(null);
      setMessages((previous) => [
        ...previous,
        { role: "user", content: submitted },
        { role: "assistant", content: demoReply(topic, language, philosopher), philosopher, demo: true },
      ]);
      setDemoTopics(topic ? demoQuestions[topic].next : demoTopics);
      setDemoTurns((value) => value + 1);
      setDraft("");
      return;
    }
    if (viaBackend ? !backendToken.trim() : !apiKey.trim()) {
      setError(errors[language][viaBackend ? "BACKEND_AUTH" : "MISSING_KEY"]); return;
    }
    locked.current = true;
    setPending(true);
    setError(null);
    setRequests((value) => value + 1);
    setMessages((previous) => [...previous, { role: "user", content: submitted }]);
    setDraft("");
    try {
      const input = {
        language, philosopher, provider, messages: submittedMessages, fictionalCase: true,
        ...(!viaBackend ? { apiKey: apiKey.trim() } : {}),
      };
      const result = viaBackend
        ? await backendChat(configuredBackend, backendToken, input)
        : await browserChat(input);
      addUsage(result.usage, result.providerRequests);
      setModel(result.model);
      setMessages((previous) => [
        ...previous, { role: "assistant", content: result.reply, philosopher, safety: result.safety },
      ]);
    } catch (error) {
      const failure = error instanceof BackendChatError ? error.failure : browserChatError(error);
      console.warn("Provider request failed.", { provider, viaBackend, code: failure.error });
      addUsage(failure.usage, failure.providerRequests);
      setError(errors[language][failure.error]);
      setMessages((previous) => previous.slice(0, -1));
      setDraft(submitted);
    } finally {
      locked.current = false;
      setPending(false);
      composer.current?.focus();
    }
  }

  function newChat() {
    if (pending || (messages.length && !window.confirm(t.reset))) return;
    setMessages([]); setDraft(""); setError(null); composer.current?.focus();
    setDemoTopics(initialDemoTopics);
  }

  function switchEngine(value: "demo" | "live") {
    if (pending || value === engine) return;
    if (messages.length && !window.confirm(t.switchEngine)) return;
    setEngine(value); setMessages([]); setDraft(""); setError(null);
    setDemoTopics(initialDemoTopics); setApiKey(""); setBackendToken(""); setConsent(false);
  }

  function switchProvider(value: Provider) {
    if (pending || value === provider) return;
    if (messages.length && !window.confirm(t.switchProvider)) return;
    setProvider(value); setMessages([]); setDraft(""); setError(null);
    setApiKey(""); setBackendToken(""); setConsent(false); setModel(DEFAULT_MODELS[value]);
  }

  function switchRoute(value: "direct" | "backend") {
    if (pending || value === greenptRoute) return;
    if (messages.length && !window.confirm(t.switchProvider)) return;
    setGreenptRoute(value); setMessages([]); setDraft(""); setError(null);
    setApiKey(""); setBackendToken(""); setConsent(false); setModel(DEFAULT_MODELS.greenpt);
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="wordmark"><span className="logo">N<span>✦</span></span><div>Nietzschian<span>AI CLINICIAN</span></div></div>
        <button className="new-chat" onClick={newChat} disabled={pending}><span>＋</span>{t.newChat}<span>↗</span></button>
        <div className="sidebar-label">{t.choosePartner}</div>
        <nav className="partners" aria-label={t.mode}>
          {(Object.keys(partners) as Philosopher[]).map((id) => (
            <button key={id} className={`partner-button ${philosopher === id ? "selected" : ""}`}
              onClick={() => setPhilosopher(id)} disabled={pending} aria-pressed={philosopher === id}>
              <Avatar philosopher={id} />
              <span><strong>{partners[id].name}</strong><small>{partners[id].description[language]}</small></span>
              {philosopher === id && <span className="selection-dot" />}
            </button>
          ))}
        </nav>
        <div className="sidebar-note"><span>↗</span><p>{t.tagline}</p><small>{t.introduction}</small></div>
        <div className="settings">
          <label className="key-label" htmlFor="chat-engine">{t.chatEngine}</label>
          <select id="chat-engine" value={engine} disabled={pending}
            onChange={(event) => switchEngine(event.target.value === "live" ? "live" : "demo")}>
            <option value="demo">{t.demo}</option>
            <option value="live">{t.live}</option>
          </select>
          <div className="language-row"><span>{t.language}</span><div className="language-toggle" aria-label={t.language}>
            {(["nl", "en"] as Language[]).map((value) => <button key={value} aria-pressed={language === value}
              disabled={pending} onClick={() => { setLanguage(value); setError(null); }}>{value.toUpperCase()}</button>)}
          </div></div>
          {engine === "demo" && <small className="key-help demo-sidebar-help">{t.demoPrivacy}</small>}
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div><h1>{t.title}</h1><p>{t.subtitle}</p></div>
          <span className="model-badge"><span />{engine === "demo" ? t.demo : `${providerNames[provider]} · ${model}`}</span>
        </header>
        <section className="connection-panel" aria-label={t.provider}>
          <div className="connection-fields">
            <label htmlFor="provider">{t.provider}
              <select id="provider" value={provider} disabled={pending}
                onChange={(event) => switchProvider(event.target.value === "greenpt" ? "greenpt" : "claude")}>
                <option value="claude">Claude (Anthropic)</option><option value="greenpt">GreenPT (EU)</option>
              </select>
            </label>
            {provider === "greenpt" && configuredBackend && <label htmlFor="greenpt-route">{t.route}
              <select id="greenpt-route" value={greenptRoute} disabled={pending}
                onChange={(event) => switchRoute(event.target.value === "backend" ? "backend" : "direct")}>
                <option value="direct">{t.directRoute}</option><option value="backend">{t.backendRoute}</option>
              </select>
            </label>}
            {viaBackend ? <label htmlFor="backend-token">{t.backendToken}
              <input id="backend-token" type="password" value={backendToken}
                onChange={(event) => setBackendToken(event.target.value)} autoComplete="off"
                spellCheck={false} disabled={pending || engine === "demo"} maxLength={300} />
            </label> : <label htmlFor="api-key">{providerNames[provider]} {t.keyTitle}
              <input id="api-key" type="password" value={apiKey} onChange={(event) => setApiKey(event.target.value)}
                placeholder={provider === "claude" ? t.keyPlaceholder : "sk-…"} autoComplete="off"
                spellCheck={false} disabled={pending || engine === "demo"} maxLength={300} />
            </label>}
            {(apiKey || backendToken) && <button className="clear-key" disabled={pending}
              onClick={() => { setApiKey(""); setBackendToken(""); }}>{t.keyClear}</button>}
          </div>
          <p>{engine === "demo" ? t.demoNotice : viaBackend ? t.backendHelp : t.keyHelp}
            {provider === "greenpt" && !viaBackend && t.providerHelp}</p>
          {engine === "live" && <small>{viaBackend ? t.backendRoute : t.endpoint}: {viaBackend
            ? `${configuredBackend}/api/chat` : PROVIDER_ENDPOINTS[provider]} · {!viaBackend && DEFAULT_MODELS[provider]}</small>}
        </section>
        <div className="chat-layout">
          <section className="conversation" aria-label={t.newChat}>
            <div className="chat-scroll">
              {engine === "demo" && <div className="demo-banner" role="note"><strong>{t.demoNotice}</strong><p>{t.demoHelp}</p></div>}
              {messages.length === 0 ? <div className="welcome">
                <div className="portrait-ring"><Avatar philosopher={philosopher} large /></div>
                <span className="eyebrow">{partner.name} · {partner.description[language]}</span>
                <h2>{t.welcome}</h2><p>{t.welcomeBody}</p>
                {engine === "live" && <div className="suggestions">{t.suggestions.map((suggestion, index) => <button key={suggestion}
                  onClick={() => { setDraft(suggestion); composer.current?.focus(); }} disabled={pending}>
                  <span className="suggestion-number">0{index + 1}</span><span>{suggestion}</span><span>↗</span>
                </button>)}</div>}
              </div> : <div className="messages" role="log" aria-live="polite" aria-relevant="additions">
                {messages.map((message, index) => <article key={index} className={`message ${message.role}`}>
                  {message.role === "assistant" ? <Avatar philosopher={message.philosopher || philosopher} /> : <span className="user-avatar">↗</span>}
                  <div><div className="message-name">{message.role === "user" ? t.you : partners[message.philosopher || philosopher].name}
                    {message.role === "assistant" && <small>{message.demo ? t.demoAssistant : t.ai}</small>}</div>
                    {message.safety && <span className="safety-badge">{t.safety}</span>}
                    <MessageContent content={message.content} /></div>
                </article>)}
              </div>}
              {engine === "demo" && <div className="demo-options" aria-label={t.demoChoices}>
                <span>{t.demoChoices}</span>
                <div className="suggestions">{demoTopics.map((topic, index) => (
                  <button key={topic} onClick={() => void send(topic)}>
                    <span className="suggestion-number">0{index + 1}</span>
                    <span>{demoQuestions[topic].label[language]}</span><span>↗</span>
                  </button>
                ))}</div>
              </div>}
              {pending && <div className="thinking" role="status"><Avatar philosopher={philosopher} /><span>{t.waiting}</span><i /><i /><i /></div>}
              <div ref={lastMessage} />
            </div>
            <div className="composer-area">
              {error && <div className="error" role="alert">{error}</div>}
              {engine === "live" && <label className="consent"><input type="checkbox" checked={consent}
                onChange={(event) => setConsent(event.target.checked)} disabled={pending} />{t.consent}</label>}
              <form className="composer" onSubmit={(event) => { event.preventDefault(); void send(); }}>
                <textarea ref={composer} aria-label={t.composer} value={draft} onChange={(event) => setDraft(event.target.value)}
                  placeholder={t.composer} maxLength={4000} disabled={pending} rows={4}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
                      event.preventDefault(); void send();
                    }
                  }} />
                <div className="composer-bottom"><span>{partner.name}<span className="composer-dot">·</span> {language.toUpperCase()}</span>
                  <button className="send" type="submit" disabled={pending || (engine === "live" && !consent) || !draft.trim()} aria-label={t.send}>↑</button></div>
              </form>
              <p className="privacy">{t.privacy}</p>
            </div>
          </section>

          <aside className="metrics" aria-label={t.stats}>
            <span className="sidebar-label">{t.stats}</span>
            <div className="request-metric"><span>{t.requestLabel}</span><strong>{format(requests).padStart(2, "0")}</strong></div>
            <div className="metric-line"><span>{t.providerLabel}</span><strong>{format(providerRequests)}</strong></div>
            <div className="metric-line"><span>{t.demoTurns}</span><strong>{format(demoTurns)}</strong></div>
            <div className="metric-divider" />
            <h3>{t.tokens}<span>↗</span></h3>
            <div className="metric-line"><span>{t.input}</span><strong>{format(usage.input)}</strong></div>
            <div className="metric-line"><span>{t.output}</span><strong>{format(usage.output)}</strong></div>
            <div className="metric-line cache"><span>{t.cache}</span><strong>{format(usage.cacheRead)} / {format(usage.cacheWrite)}</strong></div>
            <p className="metric-help">{engine === "demo" ? t.demoTokens : t.actualHelp}</p>
            <div className="estimate"><span>{engine === "demo" ? t.hypothetical : t.estimated}</span><strong>≈ {format(estimate)}</strong><small>tokens</small></div>
            <p className="metric-help">{t.estimateHelp}</p>
            <p className="metric-help">{t.estimatedOutput}</p>
            <button className="prompt-button" onClick={() => setShowPrompt(true)}>{t.prompt} <span>↗</span></button>
            <p className="metric-help privacy-note">{engine === "demo" ? t.demoPrivacy : viaBackend ? t.backendHelp : t.privacyDetail}</p>
          </aside>
        </div>
      </main>
      <dialog ref={dialog} className="prompt-modal" aria-labelledby="prompt-title"
        onCancel={() => setShowPrompt(false)} onClick={(event) => {
          if (event.target === dialog.current) setShowPrompt(false);
        }}>
          <header><h2 id="prompt-title">{t.prompt} · {language.toUpperCase()}</h2>
            <button onClick={() => setShowPrompt(false)} autoFocus>{t.close} ×</button></header>
          <pre>{systemPrompt(language, philosopher)}</pre><small>{t.portaitNote}</small>
      </dialog>
    </div>
  );
}
