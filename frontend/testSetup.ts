import { vi } from "vitest";
global.URL.createObjectURL = vi.fn(() => "blob:http://localhost/mock");