import { createContext, useContext } from 'react';

export const OpenSettingsContext = createContext<() => void>(() => {});

export function useOpenSettings() {
  return useContext(OpenSettingsContext);
}
