import { Navigate, Route, Routes } from "react-router-dom";
import { SiteShell } from "./components/SiteShell";
import { AboutPage } from "./pages/AboutPage";
import { DocumentationPage } from "./pages/DocumentationPage";
import { FeaturesPage } from "./pages/FeaturesPage";
import { HomePage } from "./pages/HomePage";
import { LabPage } from "./pages/LabPage";

export default function App() {
  return (
    <SiteShell>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/features" element={<FeaturesPage />} />
        <Route path="/documentation" element={<DocumentationPage />} />
        <Route path="/lab" element={<LabPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </SiteShell>
  );
}
