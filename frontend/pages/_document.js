import { Html, Head, Main, NextScript } from "next/document";

export default function Document() {
  return (
    <Html suppressHydrationWarning className="bg-background">
      <Head />
      <body className="antialiased bg-background">
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
