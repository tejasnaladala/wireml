const ALPHABET =
  'useandom-26T198340PX75pxJACKVERYMINDBUSHWOLF_GQZbfghjklqvwyzrict';

export function nanoid(size = 12): string {
  const bytes = new Uint8Array(size);
  crypto.getRandomValues(bytes);
  let out = '';
  for (let i = 0; i < size; i++) {
    out += ALPHABET[bytes[i]! & 63];
  }
  return out;
}
