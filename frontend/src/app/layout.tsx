import "@crayonai/react-ui/styles/index.css";
import "./custom.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "UDC Executive Dashboard",
  description: "CEO Instant Dashboard Tool — United Development Company",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
