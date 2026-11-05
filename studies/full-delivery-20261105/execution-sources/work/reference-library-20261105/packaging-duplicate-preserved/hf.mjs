import {spawn} from 'node:child_process';
const cli='C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/bin/hyperframes.mjs';
const p=spawn(process.execPath,[cli,...process.argv.slice(2)],{cwd:import.meta.dirname,windowsHide:true,stdio:'inherit',env:{...process.env,HYPERFRAMES_BROWSER_PATH:'C:/Program Files/Google/Chrome/Application/chrome.exe',HYPERFRAMES_FFMPEG_PATH:'C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe',HYPERFRAMES_FFPROBE_PATH:'C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe'}});
p.on('error',e=>{console.error(e.message);process.exit(1)});p.on('close',code=>process.exit(code??1));
