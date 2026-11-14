"use client";

import { useEffect, useState } from "react";

type Indicator = { id: string; label: string; category: string };
type Option = { id: string; label: string };
type Mission = {
  title: string;
  organisation: string;
  difficulty: string;
  estimated_minutes: number;
  simulation_notice: string;
  briefing: string;
  email: {
    display_name: string; from_address: string; reply_to: string; subject: string;
    received_label: string; body: string[]; displayed_link: string; attachment_label: string;
  };
  indicators: Indicator[];
  response_options: Option[];
  learning_objectives: string[];
};
type Assessment = {
  score: number; max_score: number; missed_indicators: string[];
  incorrect_selections: string[]; response_correct: boolean; response_explanation: string;
  feedback: { indicator_id: string; is_warning_sign: boolean; selected: boolean; identified: boolean; explanation: string }[];
  xp_awarded: number; competency_awarded: boolean; persistence: string; simulation_notice: string;
};

export default function HomePage() {
  const [mission, setMission] = useState<Mission | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [response, setResponse] = useState("");
  const [result, setResult] = useState<Assessment | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    let active = true;
    fetch("/api/demo/mission", { cache: "no-store" })
      .then(async (res) => {
        if (!res.ok) throw new Error("The demo API could not load the mission. Start the FastAPI service and retry.");
        return (await res.json()) as Mission;
      })
      .then((data) => { if (active) setMission(data); })
      .catch((reason: unknown) => { if (active) setError(reason instanceof Error ? reason.message : "Unable to load demo."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  function toggleIndicator(id: string) {
    setSelected((current) => current.includes(id) ? current.filter((item) => item !== id) : [...current, id]);
  }

  async function submit() {
    if (!response || submitting) return;
    setSubmitting(true);
    setError("");
    try {
      const res = await fetch("/api/demo/assessment", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ selected_indicator_ids: selected, response_id: response }),
      });
      const body = await res.json();
      if (!res.ok) throw new Error(body.detail?.code ?? body.message ?? "Assessment failed.");
      setResult(body as Assessment);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Assessment failed.");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <main className="shell"><p>Loading the fictional incident…</p></main>;
  if (!mission) return <main className="shell"><p className="eyebrow">CYBERQUEST · DEMO</p><h1>Phishing Detective</h1><p role="alert">{error}</p><p>Start the FastAPI demo service, then refresh this page.</p></main>;

  return (
    <main className="shell">
      <header className="topbar"><span className="brand">CYBERQUEST</span><span className="pill">ADULT LEARNING DEMO · 18+</span></header>
      <section className="hero">
        <p className="eyebrow">CYBER ACADEMY / BEGINNER MISSION</p>
        <h1>{mission.title}</h1>
        <p className="lead">A simulated incident at {mission.organisation}. Inspect the message, identify warning signs and choose a safe response.</p>
        <p className="notice">{mission.simulation_notice}</p>
      </section>
      <section className="panel">
        <div className="section-heading"><div><p className="eyebrow">01 / INCIDENT BRIEF</p><h2>Suspicious invoice notification</h2></div><span className="pill">{mission.estimated_minutes} MIN</span></div>
        <p>{mission.briefing}</p>
        <article className="email">
          <div className="email-top"><span>SIMULATED EMAIL</span><span>{mission.email.received_label}</span></div>
          <h3>{mission.email.subject}</h3>
          <dl className="mail-meta"><div><dt>From</dt><dd>{mission.email.display_name} &lt;{mission.email.from_address}&gt;</dd></div><div><dt>Reply-to</dt><dd>{mission.email.reply_to}</dd></div></dl>
          {mission.email.body.map((line, index) => <p key={index}>{line}</p>)}
          <div className="inert-link"><span>Displayed link (not clickable)</span><code>{mission.email.displayed_link}</code></div>
          <p className="muted">{mission.email.attachment_label}</p>
        </article>
      </section>
      {!result ? <>
        <section className="panel">
          <p className="eyebrow">02 / INVESTIGATE</p><h2>Which warning signs do you notice?</h2><p className="muted">Select all that apply. The server will evaluate your choices.</p>
          <div className="choice-list">{mission.indicators.map((item) => <label className="choice" key={item.id}><input type="checkbox" checked={selected.includes(item.id)} onChange={() => toggleIndicator(item.id)} /><span>{item.label}</span></label>)}</div>
        </section>
        <section className="panel">
          <p className="eyebrow">03 / RESPOND</p><h2>What should the finance team do?</h2>
          <div className="choice-list">{mission.response_options.map((item) => <label className="choice" key={item.id}><input type="radio" name="response" checked={response === item.id} onChange={() => setResponse(item.id)} /><span>{item.label}</span></label>)}</div>
          <button className="primary" disabled={!response || submitting} onClick={submit}>{submitting ? "Evaluating…" : "Submit for assessment"}</button>
          {error && <p role="alert" className="error">{error}</p>}
        </section>
      </> : <section className="panel result" aria-live="polite">
        <p className="eyebrow">04 / SERVER ASSESSMENT</p><h2>Your practice result</h2>
        <div className="score"><strong>{result.score}</strong><span>/ {result.max_score} points</span></div>
        <p>{result.response_explanation}</p>
        <h3>Indicator feedback</h3>
        <ul className="feedback">{result.feedback.map((item) => {
          const status = item.is_warning_sign ? (item.identified ? "Identified" : "Missed") : (item.selected ? "False positive" : "Neutral fact");
          return <li key={item.indicator_id}><span>{status}</span>{item.explanation}</li>;
        })}</ul>
        {result.incorrect_selections.length > 0 && <p className="muted">Review the indicators you selected that were not supported by the scenario.</p>}
        <p className="notice">{result.simulation_notice}</p>
        <p className="muted">XP awarded: {result.xp_awarded} · Competency awarded: {result.competency_awarded ? "Yes" : "No"} · Saved: {result.persistence === "not_saved" ? "No" : result.persistence}</p>
        <button className="secondary" onClick={() => { setResult(null); setSelected([]); setResponse(""); }}>Try again</button>
      </section>}
      <footer><span>Learn. Experience. Defend. Master.</span><span>Fictional scenario · No real links · No data saved</span></footer>
    </main>
  );
}
