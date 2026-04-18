import { profile } from "../content/siteContent";

export function AboutPage() {
  return (
    <div className="page-stack">
      <section className="content-panel profile-panel">
        <div className="profile-copy">
          <span className="eyebrow">about</span>
          <h1>{profile.name}</h1>
          <p className="handle-mark">branding: {profile.handle}</p>
          <p className="support-copy">{profile.bio}</p>
        </div>
        <div className="profile-mark">
          <img src="/brand-mark.svg" alt="0xchou00 mark" />
        </div>
      </section>

      <section className="content-panel card-grid three-up">
        <article className="info-card">
          <h2>Focus</h2>
          <ul className="signal-list tight-list">
            {profile.focus.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
        <article className="info-card">
          <h2>Interests</h2>
          <ul className="signal-list tight-list">
            {profile.interests.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
        <article className="info-card">
          <h2>Links</h2>
          <div className="link-stack">
            <a className="text-link" href={profile.github} target="_blank" rel="noreferrer">
              GitHub
            </a>
            <a className="text-link" href={profile.linkedin} target="_blank" rel="noreferrer">
              LinkedIn
            </a>
          </div>
        </article>
      </section>
    </div>
  );
}
