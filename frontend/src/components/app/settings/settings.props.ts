export interface SettingsProps {
  isOpen: boolean;
  onClose: (hasChanges: boolean) => void;
  hasChanges: boolean;
  setHasChanges: (hasChanges: boolean) => void;
}
