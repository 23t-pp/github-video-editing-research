import fs from'node:fs';import path from'node:path';
const base=path.resolve('work/reference-replay-v07'),meta=JSON.parse(fs.readFileSync(path.join(base,'source.json'),'utf8')).assets,geo=JSON.parse(fs.readFileSync(path.join(base,'contour-geometry.json'),'utf8')).rows;
const key=(id,f)=>geo.find(r=>r.id===id&&r.fileFrame===f).points;
const wheel=[{frame:0,points:key('B02-wheel',12)},
{frame:4,points:[[850,140],[1390,140],[1382,280],[1355,400],[1310,510],[1240,600],[1155,653],[1065,679],[991,662],[928,620],[879,555],[848,457],[833,345],[837,235]]},
{frame:8,points:[[988,140],[1590,140],[1582,327],[1550,489],[1500,625],[1430,725],[1340,784],[1240,805],[1150,779],[1079,714],[1027,613],[992,480],[977,335],[980,233]]},
{frame:12,points:key('B02-wheel',24)},
{frame:16,points:[[1085,140],[1680,140],[1672,290],[1647,425],[1600,555],[1535,671],[1450,753],[1355,794],[1268,775],[1195,710],[1144,614],[1108,490],[1084,350],[1079,233]]}];
const car=[{frame:0,points:key('B05-aircar',12)},
{frame:3,points:[[875,588],[881,580],[925,576],[930,569],[948,569],[955,575],[978,577],[992,585],[1004,602],[1010,623],[1013,648],[1009,673],[997,675],[994,659],[933,659],[926,676],[911,675],[907,658],[891,653],[881,631]]},
{frame:6,points:[[865,578],[869,569],[915,565],[921,557],[940,557],[946,562],[975,564],[991,575],[1003,590],[1009,612],[1010,637],[1004,657],[992,660],[989,643],[930,643],[925,662],[907,663],[903,646],[884,641],[872,620]]}];
for(const[id,frames,keys,band,feather]of[['B02-wheel',17,wheel,7,1.1],['B05-aircar',7,car,3,.65]]){const m=meta.find(x=>x.id===id);const spec={id,source:path.resolve(m.output),sourceIn:m.sourceIn,fps:25,assetStartFrame:12,frames,activeRect:[0,140,1920,800],mode:'grabcut',flow:'lk',grabcutBandPx:band,featherPx:feather,keyframes:keys};fs.writeFileSync(path.join(base,id+'-roto.json'),JSON.stringify(spec,null,2));}
