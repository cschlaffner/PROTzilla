# PROTzilla Frontend - Development Notes

Author: Paul Brachmann, slightly edited by Sarah Vogels

## Get Started

1. Install [node.js](https://nodejs.org/en/)
2. Install the [PNPM](https://pnpm.io/installation) package manager
   - Run `corepack enable && corepack prepare pnpm@latest --activate`
   - Run `pnpm install-completion` to install CLI auto-completion
3. After cloning the repository, run `pnpm install` in its root to install all dependencies and set up the git hooks.
4. _Optional: Configure VSCode as described in "Editor Setup" below._

_Note: See "Available Scripts" below for more information._

## Project Structure

## File Structure

All files should be named in `lower-case-with-dashes.ts`. There is no exception in casing for files holding a component.<br />
TypeScript files (usually `.ts`) using React's JSX syntax should receive a `.tsx` file extension.

The contents of this monorepo are structured in the following way:

- `.developer/`: (Config) files that ease development, e.g., [Insomnia](https://insomnia.rest/download) documents for testing
- `.github/workflows/`: GitHub Actions CI workflows
- `.husky/`: [Husky](https://typicode.github.io/husky/) config for git hooks
- `.vscode/`: [VSCode](https://code.visualstudio.com/) config
- `src/`: The application's source files
  - `app/`: The app's entry point
  - `assets/`: Assets copied over to `assets/` in distribution. Contains, e.g., the JSON translation files for i18n
  - `components/`: Application-specific React components that do not hook into the application store
  - `hooks/`: React hooks
  - `i18n/`: Internationalization helpers
  - `models/`: [MobX](https://mobx.js.org) models
  - `screens/`: All application screens accessible via their own route/as part of the navigation hierarchy
  - `services/`: Application-specific services, e.g., storage backends
  - `theme/`: The UI theme
  - `utils/`: Shared library including generic helpers
  - `constants.ts`: Application-wide constants
- `dist/`: Build artifacts (excluded from version control)

### Naming Conventions

#### Commit messages

Write a sentence-case, short (50 chars or less) summary in the imperative. Don't end with a period.
E.g.,

- `Add button component`
- `Update text styles`
- `Fix error handling`
- `Remove unused icons`

The same goes for PR titles.

#### Acronyms

In case of camel-cased acronyms, only the first letter of the acronym should be capitalized. E.g., `Player ID` should become `playerId`.

#### Attributes

- **`title` vs. `name`:** A `name` is a (locally) unique identifier that could be used to directly retrieve an object.  
  A `title` is a (user-defined) display name. The identity of an object is not bound to its `title`
- **`kind` vs. `type`:** To identify the name of a particular subtype of an object, an attribute `kind` should be used. `type` should be avoided for attribute names as it is a reserved keyword in TypeScript

#### React Component Props

Newly introduced boolean props should contain a clear prefix such as `is` or `has` to easily distinguish them from HTML attributes (e.g., `isDisabled` vs. `disabled`).

Custom event listeners should follow the `onEvent` naming convention (e.g., `onPress?: (event: PointerEvent) => void`). Change listeners that pass the changed value (as opposed to a `ChangeEvent`) should be called `onChangeText` or `onChangeValue` (for values that are not of type `string`).  
To clearly separate passing along an `onEvent` handler from implementing custom event handling logic as part of a component, custom event handlers defined in a component should follow the `handleEvent` naming schema (e.g., `handlePointerDown`).

#### CSS Class Names

Explicit CSS class names should still be used with `styled-components` to change the appearance of nested subcomponents where required (e.g., a `Button` component that contains `Icon` and `Text` components).
These class names should be written in `lower-case-with-dashes` (e.g., `focus-outline`).

## Available Scripts

### `pnpm start`

Launches a development server that runs the application in development mode.

After running this command, the app will be available at the URL printed in the console.<br />
The app will automatically reload if you change any of the source files.

### `pnpm format`

Runs automated code formatting on all applicable file types.

### `pnpm lint [--fix]`

Lints all applicable files and prints the output.<br />
`--fix` fixes all rules for which an autofix is available.

### `pnpm typecheck`

Dry-runs the TypeScript compiler.<br />
This is especially useful to check whether any types or references broke after a big refactoring.

### `pnpm test`

Runs unit tests via [Vitest](https://vitest.dev/).

Tests are automatically discovered from all `*.spec.{ts,tsx}` files.

### `pnpm storybook`

Launches [Storybook](https://storybook.js.org/).

Stories are automatically added from all `*.stories.{ts,tsx}` files.

### `pnpm build`

Builds the application.<br />
The build artifacts will be stored in the `dist/` directory.

## Editor Setup

We recommend using [VSCode](https://code.visualstudio.com/).

After opening the monorepo in VSCode, it will ask you if you want to install recommend extensions. For a seamless development experience, we recommend accepting.

## Setup

This repo includes:

- Prettier
- Eslint
- Vitest
- Husky
- GitHub Actions
- Storybook
- i18n
- React Router
- styled-components & theming
- Basic components
- MobX store set up incl. error handling & sync logic
- react-router-dom

It was generated by running:

```sh
pnpm create vite . --template react-ts
pnpm install
pnpm add -D eslint-plugin-react vitest jsdom prettier lint-staged husky @typescript-eslint/parser eslint-import-resolver-typescript eslint-plugin-import vite-plugin-svgr @testing-library/react

pnpm add i18next i18next-browser-languagedetector i18next-http-backend react-i18next moment
pnpm add -D @babel/plugin-proposal-decorators
pnpm add styled-components mobx mobx-react-lite
pnpm add react-router-dom
npx storybook@latest init
```
