import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Oral Scan | Saúde Bucal Inteligente",
  description: "Plataforma de apoio à triagem odontológica escolar e inteligência territorial.",
  manifest: "/manifest.webmanifest",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="pt-BR"><body>{children}</body></html>;
}
