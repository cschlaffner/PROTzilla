import type { Preview } from "@storybook/react";
import { useEffect, useMemo, useState } from "react";
import { styled } from "styled-components";

import { ModalRoot, NotificationCenter } from "../src/components";
import { i18n, initI18nApp } from "../src/i18n";
import { color, ColorMode, getTheme, GlobalStyles, ThemeProvider } from "../src/theme";

const Wrapper = styled.div`
  background: ${color("backgroundOffset")};
  height: 100vh;
  overflow: auto;
  width: 100%;
`;

const StyledContainer = styled.div`
  align-items: center;
  display: flex;
  justify-content: center;
  min-height: 100%;
  touch-action: none;
  width: 100%;
`;

// eslint-disable-next-line react-refresh/only-export-components
const WithThemeProvider = (
  Story: React.FC,
  { globals }: { globals: { language: string; theme: ColorMode } },
) => {
  const [isReady, setIsReady] = useState(false);
  useEffect(() => {
    void initI18nApp().then(() => {
      setIsReady(true);
    });
  }, []);

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    i18n.changeLanguage(globals.language).catch(() => {});
  }, [globals.language]);

  const theme = useMemo(() => getTheme(globals.theme), [globals.theme]);

  return (
    <ThemeProvider theme={theme}>
      <NotificationCenter>
        <Wrapper>
          <StyledContainer>
            <GlobalStyles theme={theme} />
            <ModalRoot />
            {isReady && <Story />}
          </StyledContainer>
        </Wrapper>
      </NotificationCenter>
    </ThemeProvider>
  );
};

const preview: Preview = {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  decorators: [WithThemeProvider as any],
  globalTypes: {
    theme: {
      name: "Theme",
      description: "Global theme for components",
      defaultValue: "light",
      toolbar: {
        icon: "circlehollow",
        items: ["light"],
      },
    },
    language: {
      name: "Language",
      description: "The current language",
      defaultValue: i18n.language,
      toolbar: {
        icon: "globe",
        items: ["en", "de", "cimode"],
      },
    },
  },
  parameters: {
    actions: { argTypesRegex: "^on[A-Z].*" },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    layout: "fullscreen",
    backgrounds: {
      disable: true,
    },
  },
};

export default preview;
