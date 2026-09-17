import "./globals.css";
import type { ReactNode } from "react";
export const metadata={title:"ARGONAUT AI",description:"ARGO Ocean Intelligence"};
export default function RootLayout({children}:{children:ReactNode}){return <html lang="en"><body>{children}</body></html>}
