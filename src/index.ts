// import { fromCSV } from 'rx-from-csv';
import * as PP from 'papaparse';
import * as fs from 'fs';
import * as WKT from 'wellknown';
// let parser = Parser({});
// console.warn(parser);

interface ParcelRow {
    districtna: string;
    geometry: string;
    zoning_sim?: string;
}

async function doWork() {
    let start = new Date().getTime();
    let file = fs.readFileSync('./downloads/SF_Parcels.csv', { encoding: 'utf8' });
    //console.warn(`${new Date().getTime() - start} ms`)
    let res = PP.parse(file, { header: true });
    let d = res.data as ParcelRow[];
    console.warn(d[0]);
    console.warn(`${new Date().getTime() - start} ms`);
    start = new Date().getTime();
    // await fromCSV('./downloads/SF_Parcels.csv').forEach((v) => rows.push(v as ParcelRow));
    let ids = new Map<string, number>();
    for (let v of d) {
        if (v.zoning_sim) {
            for (let v2 of v.zoning_sim.split('|')) {
                let ex = 0
                if (ids.has(v2)) {
                    ex = ids.get(v2)!! + 1
                }
                ids.set(v2, ex);
            }
        }
    }
    // let ids = [...new Set(d.map((v) => v.zoning_sim))];
    console.warn(Array.from(ids.entries()).sort((a, b) => b[1] - a[1]));
    console.warn(`${new Date().getTime() - start} ms`);
}

doWork();

