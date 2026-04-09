import { color } from "@protzilla/theme";
import { styled } from "styled-components";

export const Container = styled.div`
  width: 100%;
  height: 100vh;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const molstarTheme = {
  primary: color("protzillaDarkBlue"),
  surface: color("protzillaLightGray"),
  hover: color("secondaryHover"),
  border: color("protzillaGray"),
  lightText: color("onPrimary"),
  darkText: color("text"),
  success: color("green"),
  error: color("caution"),
};

const headers = `
  .msp-plugin .msp-sequence-select > select,
  .msp-plugin .msp-control-group-header > button,
  .msp-plugin .msp-control-group-header div,
  .msp-plugin .msp-sequence,
  .msp-plugin .msp-log-entry-info,
  .msp-plugin .msp-log-entry-warning,
  .msp-plugin .msp-section-header,
  .msp-plugin .msp-sequence-select,
  .msp-plugin ::-webkit-scrollbar-thumb,
  .msp-plugin .msp-slider-base-handle
`;

const controls = `
  .msp-plugin .msp-control-row button,
  .msp-plugin .msp-btn,
  .msp-plugin .msp-btn-link-toggle-off,
  .msp-plugin .msp-btn-link-toggle-off:active,
  .msp-plugin .msp-btn-link-toggle-off:focus,
  .msp-plugin .msp-log .msp-log-entry, 
  .msp-plugin ::-webkit-scrollbar-track,
  .msp-plugin .msp-semi-transparent-background
`;

const lightSurfaces = `
  .msp-plugin .msp-form-control,
  .msp-plugin .msp-control-row select,
  .msp-plugin .msp-control-row input[type=text],
  .msp-plugin .msp-btn-link-toggle-on,
  .msp-plugin .msp-log li,
  .msp-plugin,
  .msp-plugin .msp-sequence-wrapper-non-empty,
  .msp-plugin .msp-control-row,
  .msp-plugin .msp-control-row > div,
  .msp-plugin .msp-help-text,
  .msp-plugin .msp-flex-row,
  .msp-plugin .msp-state-image-row,
  .msp-plugin .msp-image-preview,
  .msp-plugin .msp-left-panel-controls-buttons,
  .msp-plugin .msp-layout-right,
  .msp-plugin .msp-layout-left,
  .msp-plugin .msp-highlight-info
`;

const layoutBlocks = `
  .msp-plugin .msp-log,
  .msp-plugin .msp-viewport,
  .msp-plugin .msp-layout-right,
  .msp-plugin .msp-layout-left,
  .msp-plugin .msp-slider-base-rail,
  .msp-plugin .msp-viewport-top-left-controls .msp-animation-viewport-controls .msp-animation-viewport-controls-select,
  .msp-plugin .msp-viewport-controls-panel,
`;

const elementsWithDarkText = `
  .msp-plugin .msp-viewport-controls-buttons .msp-btn-link-toggle-off,
  .msp-plugin-content,
  .msp-plugin .msp-log,
  .msp-plugin .msp-log .msp-log-timestamp,
  .msp-plugin .msp-btn-link-toggle-on,
  .msp-plugin .msp-sequence-wrapper .msp-sequence-number,
  .msp-plugin .msp-control-row > span.msp-control-row-label, 
  .msp-plugin .msp-control-row > button.msp-control-button-label,
  .msp-plugin .msp-help-text > div,
  .msp-plugin .msp-btn-action, 
  .msp-plugin .msp-btn-action:active, 
  .msp-plugin .msp-btn-action:focus,
  .msp-plugin .msp-25-lower-contrast-text,
  .msp-plugin .msp-highlight-info,
  .msp-plugin .msp-form-control:hover, 
  .msp-plugin .msp-control-row select:hover, 
  .msp-plugin .msp-control-row button:hover, 
  .msp-plugin .msp-control-row input[type=text]:hover, 
  .msp-plugin .msp-btn:hover,
  .msp-plugin .msp-btn-link-toggle-off, 
  .msp-plugin .msp-btn-link-toggle-off:active, 
  .msp-plugin .msp-btn-link-toggle-off:focus,
  ::placeholder
`;

const elementsWithLightText = `
  .msp-plugin .msp-sequence-select,
  .msp-plugin .msp-control-group-header > button, 
  .msp-plugin .msp-control-group-header div, 
  .msp-plugin .msp-section-header
`;

const hoverElements = `
  .msp-plugin .msp-btn-link-toggle-off:hover,
  .msp-plugin .msp-control-group-expander .msp-icon, 
  .msp-plugin .msp-form-control:hover, 
  .msp-plugin .msp-control-row select:hover, 
  .msp-plugin .msp-control-row button:hover, 
  .msp-plugin .msp-control-row input[type=text]:hover, 
  .msp-plugin .msp-btn:hover,
  .msp-plugin .msp-help:hover span
`;

export const CanvasWrapper = styled.div`
  flex: 1;
  position: relative;
  top: 12vh;

  && {
    /* ================= BACKGROUNDS ================= */

    ${headers} {
      background: ${molstarTheme.primary} !important;
    }

    ${controls} {
      background: ${molstarTheme.surface};
    }

    ${lightSurfaces} {
      background: ${molstarTheme.surface} !important;
    }

    ${layoutBlocks} {
      background: ${molstarTheme.border} !important;
    }

    /* ================= TEXT COLORS ================= */

    ${elementsWithDarkText} {
      color: ${molstarTheme.primary} !important;
    }

    ${elementsWithLightText} {
      color: ${molstarTheme.lightText} !important;
    }

    .msp-plugin .msp-sequence-wrapper .msp-sequence-present {
      color: ${molstarTheme.darkText} !important;
    }

    /* ================= HOVER ================= */

    ${hoverElements} {
      background: ${molstarTheme.hover} !important;
      outline: 1px solid ${molstarTheme.border} !important;
    }

    /* ================= BORDERS ================= */

    ::-webkit-scrollbar-thumb {
      border: 4px solid ${molstarTheme.primary};
    }

    .msp-plugin .msp-select-toggle::after {
      border-top-color: ${molstarTheme.primary} !important;
    }

    .msp-plugin .msp-accent-offset,
    .msp-plugin .msp-state-list > li > button:first-child {
      border-left-color: ${molstarTheme.primary} !important;
    }

    .msp-plugin .msp-transform-header-brand-purple,
    .msp-plugin .msp-transform-header-brand-blue {
      border-bottom-color: ${molstarTheme.primary} !important;
    }

    .msp-plugin .msp-slider-base-handle {
      border: 4px solid ${molstarTheme.surface} !important;
    }

    .msp-plugin .msp-layout-standard-outside .msp-layout-left {
      border-top-color: ${molstarTheme.surface} !important;
    }

    .msp-plugin .msp-layout-standard,
    .msp-plugin .msp-layout-standard-outside .msp-layout-top,
    .msp-plugin .msp-layout-standard-outside .msp-layout-bottom {
      border: 1px solid ${molstarTheme.border} !important;
    }

    .msp-plugin .msp-layout-standard-outside .msp-layout-left,
    .msp-plugin .msp-layout-standard-outside .msp-layout-right {
      border-top: 1px solid ${molstarTheme.border} !important;
    }

    .msp-plugin .msp-layout-standard-outside .msp-layout-right {
      border-left: 1px solid ${molstarTheme.border} !important;
    }

    .msp-plugin .msp-log li:not(:last-child),
    .msp-plugin .msp-layout-standard-outside .msp-layout-bottom {
      border-bottom: 1px solid ${molstarTheme.border} !important ;
    }

    .msp-plugin .msp-form-control:hover,
    .msp-plugin .msp-control-row select:hover,
    .msp-plugin .msp-control-row button:hover,
    .msp-plugin .msp-control-row input[type="text"]:hover,
    .msp-plugin .msp-btn:hover {
      outline: 1px solid ${molstarTheme.border}!important;
    }

    /* ================= SPECIAL ================= */

    .msp-plugin .msp-transform-header-brand svg {
      stroke: ${molstarTheme.primary} !important;
    }

    .msp-svg-text,
    .msp-plugin .msp-transform-header-brand svg {
      fill: ${molstarTheme.primary} !important;
    }

    /* ================= SIGNAL ================= */

    .msp-plugin .msp-btn-commit-on,
    .msp-plugin .msp-btn-commit-on:active,
    .msp-plugin .msp-btn-commit-on:focus,
    .msp-plugin .msp-log-entry-message {
      color: ${molstarTheme.success} !important;
    }

    .msp-plugin .msp-log-entry-error {
      background: ${molstarTheme.error} !important;
    }
  }
`;
