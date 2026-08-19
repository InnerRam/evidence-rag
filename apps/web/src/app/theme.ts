"use client";

import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  cssVariables: true,
  palette: {
    mode: "light",
    primary: { main: "#006f5c", dark: "#004d40", light: "#4aa994" },
    secondary: { main: "#d97706" },
    background: { default: "#f3f7f6", paper: "#ffffff" },
    text: { primary: "#142824", secondary: "#58706a" },
  },
  typography: {
    fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif',
    h1: { fontWeight: 760, letterSpacing: "-0.045em" },
    h2: { fontWeight: 720, letterSpacing: "-0.03em" },
    h3: { fontWeight: 700, letterSpacing: "-0.02em" },
    button: { textTransform: "none", fontWeight: 700 },
  },
  shape: { borderRadius: 14 },
  components: {
    MuiCard: {
      styleOverrides: {
        root: { border: "1px solid rgba(20,40,36,0.08)", boxShadow: "0 18px 50px rgba(31,63,56,0.07)" },
      },
    },
    MuiButton: { defaultProps: { disableElevation: true } },
  },
});
