// QRコードの表示（qrcode-generator）と読み取り（jsQR）を、ブラウザ用の1ファイルにまとめ直す
// qrcode-generator は MIT License、jsQR は Apache License 2.0。ライセンス文は public/vendor/LICENSES.txt
import { build } from 'esbuild';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const common = { bundle: true, minify: true, format: 'esm', target: 'es2020', legalComments: 'none' };
await build({ ...common, stdin: { contents: "import q from 'qrcode-generator'; export default q;", resolveDir: root }, outfile: resolve(root, 'public/vendor/qrcode.js') });
await build({ ...common, stdin: { contents: "import j from 'jsqr'; export default j;", resolveDir: root }, outfile: resolve(root, 'public/vendor/jsqr.js') });
console.log('public/vendor/ を作り直しました');
