// 共通デザイントークン（ただ1つの元：../design/karura-tokens.css）を取り込む
import { copyFileSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const src = resolve(here, '../../design/karura-tokens.css');
const dst = resolve(here, '../public/css/karura-tokens.css');
if (!existsSync(src)) {
  console.log('design/karura-tokens.css が見つからないので、いまあるコピーをそのまま使います');
} else {
  copyFileSync(src, dst);
  console.log('karura-tokens.css を取り込みました');
}
