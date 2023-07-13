import { isEven } from "../src/math";

test('when 2 then isEven true', () => {
    const result = isEven(2);
    expect(result).toEqual(true);
});
