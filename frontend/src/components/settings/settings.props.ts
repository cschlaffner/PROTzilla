export interface SettingsProps {
  isOpen: boolean;
  onClose: () => void;
  hasChanges: boolean;
  setHasChanges: (hasChanged: boolean) => void;
}
