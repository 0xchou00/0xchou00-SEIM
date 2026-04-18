import { NavLink } from "react-router-dom";
import { identity, primaryNav } from "../content/siteContent";

export function SiteShell({ children }) {
  return (
    <div className="site-shell">
      <div className="site-grid" />
      <header className="site-header">
        <NavLink className="brand" to="/">
          <img src="/brand-mark.svg" alt="0xchou00 mark" />
          <div>
            <span className="eyebrow">[0xchou00]</span>
            <strong>{identity.name}</strong>
          </div>
        </NavLink>
        <nav className="site-nav">
          {primaryNav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="page-shell">{children}</main>
      <footer className="site-footer">
        <span className="eyebrow">runtime model</span>
        <p>{identity.tagline}</p>
      </footer>
    </div>
  );
}
