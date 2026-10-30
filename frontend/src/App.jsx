import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  Activity, ArrowDownRight, ArrowUpRight, AudioLines, BookOpen, Check,
  ChevronDown, CircleHelp, Fingerprint, Github, Ghost, LockKeyhole,
  Menu, Moon, Play, Settings, Shield, ShieldAlert,
  ShieldCheck, Sparkles, Terminal, X,
} from "lucide-react";

const scenarios = {
  "dangerous-command": {
    command: "rm -rf node_modules",
    risk: "DANGEROUS",
    tone: "danger",
    output: "GhostGuard detected recursive deletion.",
    detail: "This operation recursively removes files. Dangerous commands are blocked without an override.",
    next: "No command was executed in this simulated public demonstration.",
    alt: "Review project-specific cleanup instructions before removing files.",
  },
  "port-conflict": {
    command: "npm run dev",
    risk: "SAFE",
    tone: "safe",
    output: "EADDRINUSE: address already in use :::3000",
    detail: "The simulated development server cannot bind to port 3000.",
    next: "Possible cause: another development server may already be running.",
    alt: "Get-NetTCPConnection -LocalPort 3000 — inspect the associated process.",
  },
  "missing-dependency": {
    command: "npm run dev",
    risk: "SAFE",
    tone: "safe",
    output: "Error: Cannot find module 'vite'",
    detail: "Node.js reports that the Vite package could not be resolved.",
    next: "Possible cause: dependencies have not been installed, or Vite is missing from package.json.",
    alt: "Inspect package.json and installed dependencies before choosing whether to install.",
  },
};

const navItems = [
  ["Overview", Activity],
  ["Terminal demo", Terminal],
  ["Security center", ShieldCheck],
  ["Settings", Settings],
];

function GhostMark({ small = false }) {
  return <span className={`ghost-mark ${small ? "ghost-mark-sm" : ""}`}><Ghost size={small ? 17 : 20} /></span>;
}

function Sidebar({ page, setPage, open, onClose }) {
  return (
    <aside className={`sidebar ${open ? "sidebar-open" : ""}`}>
      <div className="brand"><GhostMark /><span>ghost<span className="brand-light">shell</span></span><button className="mobile-close icon-button" onClick={onClose}><X size={18} /></button></div>
      <div className="workspace-label">LOCAL WORKSPACE</div>
      <div className="workspace-card"><span className="workspace-dot" /><span><b>Public sandbox</b><small>Browser simulation</small></span><ChevronDown size={15} /></div>
      <div className="nav-label">WORKSPACE</div>
      <nav className="side-nav">
        {navItems.map(([label, Icon]) => (
          <button key={label} className={`nav-item ${page === label ? "active" : ""}`} onClick={() => { setPage(label); onClose(); }}>
            <Icon size={17} strokeWidth={1.8} /><span>{label}</span>{label === "Terminal demo" && <span className="demo-tag">DEMO</span>}
          </button>
        ))}
      </nav>
      <div className="sidebar-bottom">
        <div className="privacy-card"><div className="privacy-icon"><LockKeyhole size={15} /></div><div><b>No shell is connected.</b><p>Demo scenarios use fixed sample data.</p></div></div>
        <a className="github-link" href="https://github.com/" target="_blank" rel="noreferrer"><Github size={16} /> View on GitHub <ArrowUpRight size={14} /></a>
        <div className="version-row"><span>GHOSTSHELL</span><span>v0.1.0</span></div>
      </div>
    </aside>
  );
}

function Topbar({ page, onMenu }) {
  return <header className="topbar"><button className="mobile-menu icon-button" onClick={onMenu}><Menu size={19} /></button><div className="breadcrumb"><span>Workspace</span><span className="slash">/</span><b>{page}</b></div><div className="top-actions"><span className="local-pill"><span /> STATIC DEMO</span><button className="icon-button help-button" aria-label="Help"><CircleHelp size={17} /></button><span className="avatar">G</span></div></header>;
}

function StatusStrip() {
  return <div className="status-strip"><div className="status-item"><span className="status-dot green" /><span>GhostGuard</span><b>Demo</b></div><i /><div className="status-item"><span className="status-dot amber" /><span>AI model</span><b>Not connected</b></div><i /><div className="status-item"><LockKeyhole size={14} /><span>Privacy</span><b>No command data</b></div><button className="connect-link" onClick={() => document.getElementById("ollama-setup")?.scrollIntoView({ behavior: "smooth" })}>Set up Ollama <ArrowUpRight size={13} /></button></div>;
}

function TerminalPreview() {
  const [lines, setLines] = useState([]);
  const run = (key) => setLines((current) => [...current.slice(-4), { ...scenarios[key], id: Date.now() }]);
  return <section className="terminal-card" id="terminal-demo">
    <div className="terminal-head"><div className="window-lights"><i /><i /><i /></div><div className="terminal-title"><Terminal size={14} /> ghost@localhost <span>—</span> powershell</div><span className="terminal-label"><span /> SIMULATED DEMO</span></div>
    <div className="terminal-body">
      <div className="terminal-welcome"><span className="prompt-mark">✳</span><span>GhostShell sandbox ready. Choose a scenario to see GhostGuard in action.</span></div>
      <AnimatePresence initial={false}>{lines.map((line) => <motion.div key={line.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="terminal-result">
        <div className="terminal-command"><span className="terminal-prompt">PS</span><span>›</span><code>{line.command}</code><span className={`risk-badge ${line.tone}`}>{line.risk}</span></div>
        <div className={`terminal-output ${line.tone}`}>{line.output}</div>
        <div className="ghost-reply"><Ghost size={15} /><div><b>The ghost noticed something.</b><p>{line.detail} {line.next}</p><small>Suggested next step · <code>{line.alt}</code></small></div></div>
      </motion.div>)}</AnimatePresence>
    </div>
    <div className="terminal-actions">
      <span className="scenario-label">RUN A SCENARIO</span>
      <button onClick={() => run("dangerous-command")}><ShieldAlert size={14} /> Dangerous command</button>
      <button onClick={() => run("port-conflict")}><Activity size={14} /> Port conflict</button>
      <button onClick={() => run("missing-dependency")}><CircleHelp size={14} /> Missing dependency</button>
    </div>
  </section>;
}

function Overview({ page, setPage }) {
  return <>
    <div className="demo-callout preview-note"><ShieldCheck size={17} /><span><b>Public interactive preview</b><small>Scenarios are simulated in your browser. The local CLI and Ollama are not connected to this site.</small></span></div>
    <StatusStrip />
    <section className="hero-row">
      <div><div className="eyebrow"><span className="eyebrow-line" /> A DIFFERENT KIND OF TERMINAL COMPANION</div><h1>YOUR TERMINAL<br />HAS A <em>SOUL.</em></h1><p className="hero-copy">A local-first AI guardian that watches your commands, investigates errors, and protects your development environment.</p><div className="hero-buttons"><button className="primary-button" onClick={() => { setPage("Terminal demo"); document.getElementById("terminal-demo")?.scrollIntoView({ behavior: "smooth" }); }}><Play size={15} fill="currentColor" /> Explore GhostShell</button><a className="secondary-button" href="https://github.com/" target="_blank" rel="noreferrer"><Github size={16} /> View on GitHub</a></div><div className="hero-proof"><span><ShieldCheck size={14} /> Deterministic command guard</span><span><LockKeyhole size={14} /> Local inference</span></div></div>
      <div className="ghost-art" aria-hidden="true"><div className="art-orbit orbit-a" /><div className="art-orbit orbit-b" /><div className="ghost-glow" /><div className="ghost-figure"><div className="ghost-sheet"><i /><i /><b /></div></div><div className="art-coordinate">GHS / 001<br /><span>LOCAL ENTITY</span></div><div className="art-signal"><AudioLines size={17} /> SIGNAL DETECTED</div></div>
    </section>
    <section className="metrics-grid">
      <div className="metric-card"><div className="metric-top"><Shield size={17} /><span>COMMAND GUARD</span></div><strong>Deterministic</strong><small>Rules first. No AI override.</small><div className="metric-line"><span style={{ width: "82%" }} /></div></div>
      <div className="metric-card"><div className="metric-top purple"><Sparkles size={17} /><span>LOCAL AI</span></div><strong>Gemma 3 · 1B</strong><small>Through Ollama on your machine</small><div className="metric-line purple-line"><span style={{ width: "64%" }} /></div></div>
      <div className="metric-card"><div className="metric-top blue"><Fingerprint size={17} /><span>SESSION MEMORY</span></div><strong>Stored locally</strong><small>SQLite · redacted history</small><div className="metric-line blue-line"><span style={{ width: "91%" }} /></div></div>
    </section>
    <div className="section-heading"><div><div className="eyebrow">SEE THE GHOST AT WORK</div><h2>A safer way to troubleshoot.</h2></div><button className="text-button" onClick={() => setPage("Terminal demo")}>Open full demo <ArrowUpRight size={14} /></button></div>
    <TerminalPreview />
    <section className="lower-grid">
      <div className="feature-card"><div className="feature-icon green-icon"><ShieldCheck size={18} /></div><h3>Protection before execution</h3><p>Every command is classified by deterministic rules. Dangerous operations are denied; caution commands need one-time approval.</p><button className="text-button" onClick={() => setPage("Security center")}>Explore GhostGuard <ArrowUpRight size={13} /></button></div>
      <div className="feature-card"><div className="feature-icon purple-icon"><Sparkles size={18} /></div><h3>Local intelligence, your way</h3><p>Gemma through Ollama investigates errors on your device. Missing model? Safety still works without the AI.</p><a className="text-button" href="#ollama-setup">Set up local AI <ArrowDownRight size={13} /></a></div>
      <div className="feature-card"><div className="feature-icon blue-icon"><BookOpen size={18} /></div><h3>Built for real workflows</h3><p>Useful terminal context, a small supported command set, three ghost personalities, and privacy-first session memory.</p><button className="text-button" onClick={() => setPage("Settings")}>Explore settings <ArrowUpRight size={13} /></button></div>
    </section>
    <section className="architecture-section">
      <div className="section-heading"><div><div className="eyebrow">HOW THE GHOST WORKS</div><h2>Local AI. Locally guarded.</h2></div><span className="architecture-tag"><LockKeyhole size={12} /> NO CLOUD AI</span></div>
      <div className="architecture-flow">
        <div className="architecture-node"><div className="feature-icon blue-icon"><Terminal size={17} /></div><b>Your terminal</b><small>Supported command input</small></div>
        <div className="architecture-connector"><span /> review <ArrowUpRight size={12} /></div>
        <div className="architecture-node guard-node"><div className="feature-icon green-icon"><ShieldCheck size={17} /></div><b>GhostGuard</b><small>Deterministic policy + approval</small></div>
        <div className="architecture-connector"><span /> redacted evidence <ArrowUpRight size={12} /></div>
        <div className="architecture-node"><div className="feature-icon purple-icon"><Sparkles size={17} /></div><b>Ollama + Gemma</b><small>Optional local explanation</small></div>
      </div>
      <p className="architecture-footnote">The model can explain an error. It cannot approve or execute a command. Public demo scenarios never leave this browser simulation.</p>
    </section>
    <section className="landing-bottom-grid">
      <div className="install-panel" id="install"><div className="eyebrow">GET STARTED LOCALLY</div><h2>Wake the ghost.</h2><p>Python 3.11+ · Ollama optional for safety features</p><div className="install-commands"><code><span>01</span> python -m pip install -r requirements.txt</code><code><span>02</span> ollama pull gemma3:1b <i># optional local AI</i></code><code><span>03</span> python -m app.cli</code></div><small>Install Ollama separately if you want local Gemma explanations. The CLI works without it.</small></div>
      <div className="privacy-panel"><div className="feature-icon green-icon"><LockKeyhole size={17} /></div><div className="eyebrow">PRIVACY BY DESIGN</div><h2>Your terminal stays yours.</h2><p>Local SQLite history is redacted before storage. When enabled, Gemma receives bounded, redacted evidence through Ollama on your machine—never a mandatory cloud AI service.</p><div className="privacy-check"><Check size={14} /> No command execution on the public site</div><div className="privacy-check"><Check size={14} /> No automatic AI-generated commands</div><div className="privacy-check"><Check size={14} /> Local model and history stay on your machine</div></div>
    </section>
    <section className="tech-section"><div className="eyebrow">BUILT WITH OPEN TOOLS</div><div className="tech-list"><span>PYTHON</span><span>FASTAPI</span><span>OLLAMA</span><span>GEMMA 3</span><span>SQLITE</span><span>REACT</span><span>VITE</span><span>TAILWIND</span></div></section>
  </>;
}

function DemoPage() {
  return <><PageHeading eyebrow="SAFE TO EXPLORE" title="The sandbox terminal." description="These scenarios are simulated in your browser. No shell is connected, and nothing runs on this server or your computer." /><div className="demo-callout"><ShieldCheck size={17} /><span><b>Public demo · execution disabled</b><small>Predefined examples only. This interface cannot execute commands.</small></span></div><TerminalPreview /></>;
}

function PageHeading({ eyebrow, title, description }) {
  return <div className="page-heading"><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div>;
}

function SecurityPage() {
  return <><PageHeading eyebrow="SECURITY CENTER" title="A guardian, not a gatekeeper." description="GhostGuard's security decisions are deterministic and separate from AI-generated explanations." /><div className="security-banner"><div className="security-shield"><ShieldCheck size={24} /></div><div><span className="security-kicker">GHOSTGUARD STATUS</span><h2>Protection is active.</h2><p>Commands are reviewed before the controlled runner can execute them.</p></div><span className="active-pill"><span /> ACTIVE</span></div><div className="security-grid"><div className="security-card"><ShieldAlert size={18} className="red-text" /><h3>Risk classifications</h3><p><b className="green-text">SAFE</b> · Known read-only commands</p><p><b className="amber-text">CAUTION</b> · One-time human approval</p><p><b className="red-text">DANGEROUS</b> · Blocked by default</p></div><div className="security-card"><LockKeyhole size={18} className="green-text" /><h3>Private by design</h3><p>History is stored in local SQLite. Secrets are redacted before persistence and model prompts.</p><p>Ollama inference stays on the local machine; no cloud AI fallback.</p></div><div className="security-card"><Terminal size={18} className="purple-text" /><h3>Restricted execution</h3><p>Explicit command set, argument lists, <code>shell=False</code>, process timeout, and bounded output.</p><p>The public demo has no execution endpoint.</p></div><div className="security-card"><CircleHelp size={18} className="blue-text" /><h3>Honest limitations</h3><p>Command parsing is conservative but cannot guarantee protection from every operating-system or tool behavior.</p><p>Review every approval and keep backups.</p></div></div><a className="documentation-card" href="https://github.com/" target="_blank" rel="noreferrer"><BookOpen size={18} /><span><b>Read the security notes</b><small>Threat model, limits, and safe usage.</small></span><ArrowUpRight size={16} /></a></>;
}

function SettingsPage() {
  const [personality, setPersonality] = useState("Guardian");
  const [model, setModel] = useState("gemma3:1b");
  const [retention, setRetention] = useState("30");
  const [verbose, setVerbose] = useState(true);
  return <><PageHeading eyebrow="PREFERENCES" title="Make it yours." description="Personalize how GhostShell talks and remembers. The security policy does not change with your preferences." /><div className="settings-layout"><div className="settings-card"><div className="settings-title"><GhostMark small /><div><h3>Ghost personality</h3><p>Changes narration, never security decisions.</p></div></div><div className="personality-options">{["Ancient", "Cursed", "Guardian"].map((item) => <button key={item} className={personality === item ? "selected" : ""} onClick={() => setPersonality(item)}><span className={`personality-orb ${item.toLowerCase()}`}><Ghost size={17} /></span><span><b>{item}</b><small>{item === "Ancient" ? "Calm & wise" : item === "Cursed" ? "Witty & spooky" : "Protective & serious"}</small></span>{personality === item && <Check size={16} />}</button>)}</div></div>  <div className="settings-card"><div className="settings-title"><div className="feature-icon purple-icon"><Sparkles size={17} /></div><div><h3>Local AI model</h3><p>Inference runs through Ollama on this device.</p></div></div><div className="setting-row"><span><b>Model</b><small>Preview only; configure GHOSTSHELL_MODEL locally</small></span><select value={model} onChange={(event) => setModel(event.target.value)}><option value="gemma3:1b">gemma3:1b</option><option value="gemma2:2b">gemma2:2b</option><option value="llama3.2:1b">llama3.2:1b</option></select></div><div className="setting-row"><span><b>Ollama connection</b><small>http://127.0.0.1:11434</small></span><span className="disconnected"><span /> Not detected</span></div><div className="setup-note" id="ollama-setup"><b>Get started</b><code>ollama pull gemma3:1b</code><small>Install and start Ollama first. The terminal guard works without a model.</small></div></div><div className="settings-card"><div className="settings-title"><div className="feature-icon blue-icon"><BookOpen size={17} /></div><div><h3>Session memory</h3><p>Stored in a local SQLite database. Never uploaded.</p></div></div><div className="setting-row"><span><b>History retention</b><small>Most recent command records</small></span><select value={retention} onChange={(event) => setRetention(event.target.value)}><option value="10">10 entries</option><option value="30">30 entries</option><option value="100">100 entries</option></select></div><div className="setting-row"><span><b>Detailed responses</b><small>Include extra troubleshooting context</small></span><button className={`toggle ${verbose ? "on" : ""}`} onClick={() => setVerbose(!verbose)} aria-label="Toggle detailed responses"><span /></button></div><div className="setting-row"><span><b>Appearance</b><small>Atmospheric dark interface</small></span><span className="setting-value"><Moon size={14} /> Dark <Check size={14} /></span></div></div></div></>;
}

function App() {
  const [page, setPage] = useState("Overview");
  const [menuOpen, setMenuOpen] = useState(false);
  return <div className="app-shell"><div className={`sidebar-scrim ${menuOpen ? "visible" : ""}`} onClick={() => setMenuOpen(false)} /><Sidebar page={page} setPage={setPage} open={menuOpen} onClose={() => setMenuOpen(false)} /><div className="main-area"><Topbar page={page} onMenu={() => setMenuOpen(true)} /><main className="content"><AnimatePresence mode="wait"><motion.div key={page} initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -4 }} transition={{ duration: 0.18 }}>{page === "Overview" ? <Overview page={page} setPage={setPage} /> : page === "Terminal demo" ? <DemoPage /> : page === "Security center" ? <SecurityPage /> : <SettingsPage />}</motion.div></AnimatePresence><footer className="page-footer"><span>GHOSTSHELL © 2026</span><span>Your terminal has a soul. And this time, it's here to protect you.</span><a href="https://github.com/" target="_blank" rel="noreferrer">Open source <ArrowUpRight size={12} /></a></footer></main></div></div>;
}

export default App;
