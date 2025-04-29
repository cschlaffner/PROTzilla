export interface SettingsProps {
  isOpen: boolean;
  onClose: () => void;
  setHasChanges: (hasChanged: boolean) => void;
}
