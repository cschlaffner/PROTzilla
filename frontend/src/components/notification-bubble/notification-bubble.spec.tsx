import { render } from "@testing-library/react";

import { NotificationBubble } from "./notification-bubble";

describe("NotificationBubble", () => {
  it("should render successfully", () => {
    const { baseElement } = render(<NotificationBubble notifications={5} />);
    expect(baseElement).toBeTruthy();
  });
});
