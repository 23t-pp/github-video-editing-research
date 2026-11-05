import fs from 'node:fs';
import {spawn} from 'node:child_process';

const cli = process.env.HYPERFRAMES_CLI || 'C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/bin/hyperframes.mjs';
if (!fs.existsSync(cli)) {
  throw Error('请将 HYPERFRAMES_CLI 设为本机 hyperframes.mjs 的路径。');
}
const local = {
  HYPERFRAMES_BROWSER_PATH: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  HYPERFRAMES_FFMPEG_PATH: 'C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe',
  HYPERFRAMES_FFPROBE_PATH: 'C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe'
};
const env = {...process.env};
for (const [key, value] of Object.entries(local)) {
  if (!env[key] && fs.existsSync(value)) env[key] = value;
}
const child = spawn(process.execPath, [cli,...process.argv.slice(2)], {
  cwd: import.meta.dirname, windowsHide: true, stdio: 'inherit', env
});
child.on('error', error => { console.error(error.message); process.exitCode = 1; });
child.on('close', code => { process.exitCode = code ?? 1; });
