import { Component, HostListener, Inject, Input, OnInit, QueryList, ViewChildren } from '@angular/core';
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

import { ActivatedRoute, Router } from '@angular/router';
import {
  ApexAxisChartSeries,
  ApexChart,
  ApexXAxis,
  ApexDataLabels,
  ApexTitleSubtitle,
  ApexStroke,
  ApexGrid
} from "ng-apexcharts";
import { ServerService } from 'src/app/server.service';
import { __values } from 'tslib';
import { BurstTableComponent } from '../components/burst-table/burst-table.component';

export type ChartOptions = {
  series: ApexAxisChartSeries;
  chart: ApexChart;
  xaxis: ApexXAxis;
  dataLabels: ApexDataLabels;
  grid: ApexGrid;
  stroke: ApexStroke;
  title: ApexTitleSubtitle;
}
export interface statModelParams {
  is_fit: boolean,
  ChiSq: number,
  A: number,
  B: number,
  C: number,
  D: number,
  Duration: number,
}
export interface totalData {
  start: number,
  flare_count: number,
  lc_data: point[],
  ptlineData: point[],
  file_name: string,
  chartSeries: ApexAxisChartSeries,
  Decay: number,
  Rise: number
}
export interface statModelData {
  plot_base64: string,
  is_detected: boolean,
  fit_params: statModelParams,
  duration: number
}
export interface burstRow {
  bg_rate: number,
  peak_time: number,
  peak_temp: number,
  peak_flux: number,
  peak_em: number,
  peak_rate: number,
  ml_conf: number,
  lm: statModelData,
  ns: statModelData,
  class: string,
  total_lrad: number
}
export interface point {
  x: number,
  y: number | null
}
@Component({
  selector: 'app-report',
  templateUrl: './report.component.html',
  styleUrls: ['./report.component.scss']
})
export class ReportComponent implements OnInit {
  @Input('data') data: number[][][] = []
  @Input('editable') editable: boolean = false;
  @ViewChildren('burstTable') burstTable!: QueryList<BurstTableComponent>
  rejectedBursts: number[] = []
  burstListEditable: boolean = false;
  totalChartMode: number = 3;
  burstsDecoded: boolean = false;
  public chartOptions: Partial<ChartOptions>[] = []
  public tableChartOptions: Partial<ChartOptions>[] = []
  metaData: any[] = [];
  tableData: any[] = [];
  binSzMin: number = 50;
  binSzMax: number = 250;
  binSzValue: number = 200;
  varSzMin: number = 5;
  varSzMax: number = 50;
  varSzValue: number = 10;
  printing: boolean = false;

  burstSelectionModes = [
    { viewValue: 'N-Sigma', value: 0 },
    { viewValue: 'Local Maxima', value: 1 },
    { viewValue: 'N-Sigma ∩ Local Maxima', value: 2 },
    { viewValue: 'N-Sigma ∪ Local Maxima', value: 3 },
  ]
  @HostListener('window:resize', ['$event'])
  OnResize(event: any) {
    this.innerWidth = window.innerWidth;
  }
  formatSeconds(totalSeconds: number) {
    let days = Math.floor(totalSeconds / (3600 * 24))
    totalSeconds %= (24 * 3600)
    let hours = Math.floor(totalSeconds / 3600);
    totalSeconds %= 3600;
    let minutes = Math.floor(totalSeconds / 60);
    let seconds = Math.round(totalSeconds % 60);
    return `${days}:${hours}:${minutes}:${seconds}`
  }
  mapClass: Function = (burst: number[][]) => {
    if (this.rejectedBursts.includes(this.data.indexOf(burst))) {
      return 'disabled';
    }
    return ''
  }
  totalData!: totalData;

  saveData() {
    let btns = document.querySelectorAll('button')
    this.printing = true;
    for (let i = 0; i < btns.length; i++) {
      btns.item(i).style.display = 'none';
    }
    let tempwidth = this.innerWidth;
    this.innerWidth = 0.6 * tempwidth;
    this.updateTotalData()

    setTimeout(() => {
      window.print()
      for (let i = 0; i < btns.length; i++) {
        btns.item(i).style.display = '';
      }
      this.printing = false

    }, 3000)

  }
  trainModel() {
    let ptbursts = this.sortBurstArray(this.sortables[1].value, this.sortables[1].value)
    let boolArray = ptbursts.map((v, j, []) => {
      if (this.rejectedBursts.includes(this.bursts.indexOf(v))) { return 0 }
      else { return 1 }
    })
    this.server.trainModel(boolArray).subscribe(v => {
      this.allowUnload = true;
      window.location.reload()
    })
  }
  formatLabel(value: number) {
    return Math.round(value);
  }
  resubmit() {
    this.allowUnload = true;
    window.location.href = `report/${this.binSzValue}`
  }
  innerWidth: number = window.innerWidth;
  displayedColumns!: string[];
  invertEditable() {
    this.burstListEditable = !this.burstListEditable
    for (let i = 0; i < this.burstTable.length; i++) {
      this.burstTable.toArray()[i].burstListEditable = !this.burstTable.toArray()[i].burstListEditable
    }
  }
  filterAccepted(data: Partial<burstRow>[]) {
    return data.filter((v, i, []) => !this.rejectedBursts.includes(i));
  }
  filterRejected(data: Partial<burstRow>[]) {
    return data.filter((v, i, []) => this.rejectedBursts.includes(i))
  }

  removeBurst(ev: number) {
    this.rejectedBursts.push(ev)
    this.burstTable.toArray()[1].rejectedBursts.push(ev)
  }
  addBurst(ev: number) {
    this.rejectedBursts.splice(this.rejectedBursts.indexOf(ev), 1)
    this.burstTable.toArray()[0].rejectedBursts.splice(this.burstTable.toArray()[0].rejectedBursts.indexOf(ev), 1)
  }
  openPanel(burstIndex: number) {
    const dialogRef = this.dialog.open(DialogOptionsDialog, {
      data: {
        burst: this.data[burstIndex],
        burstIndex: burstIndex,
        chartOptions: this.chartOptions[burstIndex],
        metaData: this.metaData[burstIndex],
        accentColor: this.accentColor,
        primaryColor: this.primaryColor,
        displayedColumns: this.displayedColumns
      }
    });
    dialogRef
  }
  cleanedData(data: Partial<burstRow>[]) {
    let cleaned = data.map((burst: Partial<burstRow>, j, []) => {
      let obj = { ...burst }
      let ns = obj.ns; let lm = obj.lm;
      if (ns?.is_detected && ns.fit_params.is_fit) {
        obj.ns = {
          ...ns,
          fit_params: {
            ...ns.fit_params,
            A: Number.parseFloat(ns.fit_params.A.toPrecision(2)),
            B: Number.parseFloat(ns.fit_params.B.toPrecision(2)),
            C: Number.parseFloat(ns.fit_params.C.toPrecision(2)),
            D: Number.parseFloat(ns.fit_params.D.toPrecision(2)),
            ChiSq: Number.parseFloat(ns.fit_params.ChiSq.toPrecision(2)),
            Duration: Math.round(ns.fit_params.Duration * 100) / 100
          }
        }
      }
      if (lm?.is_detected && lm.fit_params.is_fit) {
        obj.lm = {
          ...lm,
          fit_params: {
            ...lm.fit_params,
            A: Number.parseFloat(lm.fit_params.A.toPrecision(2)),
            B: Number.parseFloat(lm.fit_params.B.toPrecision(2)),
            C: Number.parseFloat(lm.fit_params.C.toPrecision(2)),
            D: Number.parseFloat(lm.fit_params.D.toPrecision(2)),
            ChiSq: Number.parseFloat(lm.fit_params.ChiSq.toPrecision(2)),
            Duration: Math.round(lm.fit_params.Duration * 100) / 100
          }
        }
      }
      obj.bg_rate = Math.round(100 * obj.bg_rate!) / 100
      obj.ml_conf = Math.round(100 * obj.ml_conf!) / 100
      obj.peak_rate = Math.round(100 * obj.peak_rate!) / 100
      obj.peak_time = Math.round(obj.peak_time!)
      return obj
    }
    )
    return cleaned;
  }
  constructor(public dialog: MatDialog,
    private server: ServerService,
    private router: Router,
    private route: ActivatedRoute) {
  }
  sortableIndex: number = 0
  scatterData!: any[]
  lineData!: any[]
  bursts: Partial<burstRow>[] = []
  mapChartOptions!: Function
  sortables = [
    { viewValue: 'Peak Count Rate', value: 'peak_rate' },
    { viewValue: 'Peak Time', value: 'peak_time' },
    { viewValue: 'Peak Flux', value: 'peak_flux' },
    { viewValue: 'Peak Temp', value: 'peak_temp' },
    { viewValue: 'ML Confidence', value: 'ml_conf' },
  ]

  allowUnload: boolean = false;
  public accentColor: string = '#ffd640';
  public primaryColor: string = '#683ab7';
  @HostListener('window:beforeunload', ['$event'])
  unloadHandler(event: Event) {
    if (!this.allowUnload) {
      window.opener.location.reload();
    }

  }
  stringMap(burst1: Partial<burstRow>): Map<string, number> {
    let map = new Map<string, number>();
    map.set('peak_time', burst1.peak_time!)
    map.set('peak_rate', burst1.peak_rate!)
    map.set('peak_temp', burst1.peak_temp!)
    map.set('peak_flux', burst1.peak_flux!)
    map.set('peak_em', burst1.peak_em!)
    map.set('ml_conf', burst1.ml_conf!)
    map.set('class', -burst1.class?.charCodeAt(0)!)
    return map;
  }
  sortBurstArray(key: string, tbk: string) {
    return this.bursts.sort((burst1: Partial<burstRow>, burst2: Partial<burstRow>) => {
      let map1 = this.stringMap(burst1)
      let map2 = this.stringMap(burst2)
      let compval = (map1.get(key)! - map2.get(key)!)
      if (compval === 0) {
        compval = (map2.get(tbk)! - map1.get(tbk)!)
      }
      if (key === 'peak_time') {
        return compval;
      } else {
        return -compval;
      }
    })
  }
  sortBursts(value: string) {

    let RBursts = this.filterRejected(this.bursts)
    let key = value
    let tieBreakerKey = 'peak_time';
    this.rejectedBursts = []
    this.bursts = this.sortBurstArray(key, tieBreakerKey)
    this.rejectedBursts = RBursts.map(v => this.bursts.indexOf(v));
  }
  getDate(moment: number) {
    let date = new Date();
    date.setTime(moment * 1000)
    let parts = date.toISOString().split('T')
    parts[1] = parts[1].slice(0, -5)
    return parts.join(' ')
  }
  totalChartReady: boolean = false;
  updateTotalData(value?: number) {
    this.totalChartReady = false;
    this.totalData = {
      ...this.totalData,
      start: Math.round(this.totalData.start * 100) / 100,
      ptlineData: this.bursts.filter(burst => [
        burst.ns?.is_detected,
        burst.lm?.is_detected,
        burst.ns?.is_detected && burst.lm?.is_detected,
        burst.ns?.is_detected || burst.lm?.is_detected,
      ][value != null ? value : this.totalChartMode]).map(burst => { return { x: burst.peak_time, y: burst.peak_rate } as point; })
    };
    this.totalData.chartSeries = [
      {
        name: 'Peaks',
        data: this.totalData.ptlineData.map(obj => [obj.x, obj.y]),
        type: 'scatter'
      },
      {
        name: 'All points',
        data: this.totalData.lc_data.map(obj => [obj.x, obj.y]),
        type: 'line'
      }
    ] as ApexAxisChartSeries
    setTimeout(() => {
      this.totalChartReady = true;
    }, 500)
  }
  revertToUploadPage() {
    this.allowUnload = true;
    window.location.href = '/upload'
  }
  ngOnInit(): void {
    let binsize = JSON.parse(JSON.stringify(this.route.snapshot.paramMap.get('binsize') || '{}'));
    this.binSzValue = binsize
    this.server.getBursts(binsize).subscribe((data: any) => {
      this.bursts = this.cleanedData(data.flares)
      this.totalData = {
        ...data.total,
        start: Math.round(data.total.start * 100) / 100,
        ptlineData: this.bursts.filter(burst =>
          [
            burst.ns!.is_detected,
            burst.lm!.is_detected,
            (burst.lm!.is_detected && burst.ns!.is_detected),
            (burst.lm!.is_detected || burst.ns!.is_detected)
          ][this.totalChartMode]
        ).map(burst => {
          return {
            'x': burst.peak_time,
            'y': burst.peak_rate
          }
        })
      };
      this.totalData.chartSeries = [
        {
          name: 'Peaks',
          data: this.totalData.ptlineData.map(obj => [obj.x, obj.y]),
          type: 'scatter'
        },
        {
          name: 'All points',
          data: this.totalData.lc_data.map(obj => [obj.x, obj.y]),
          type: 'line'
        }
      ] as ApexAxisChartSeries
      this.burstsDecoded = true;
      this.totalChartReady = true;
    })
    this.innerWidth = window.innerWidth;
  }
  @HostListener('window:resize', ['$event'])
  onResize(event: any) {
    this.totalChartReady = false
    this.innerWidth = window.innerWidth;
    setTimeout(() => this.totalChartReady = true, 500)
  }
}
export interface DialogData {
  burst: number[][];
  burstIndex: number;
  metaData: any;
  chartOptions: Partial<ChartOptions>;
  displayedColumns: string[]
  accentColor: string;
  primaryColor: string;
}
@Component({
  selector: 'dialog-options',
  templateUrl: './dialog-options.html',
  styleUrls: ['./report.component.scss']
})
export class DialogOptionsDialog implements OnInit {
  constructor(
    public dialogRef: MatDialogRef<DialogOptionsDialog>,
    @Inject(MAT_DIALOG_DATA) public data: DialogData,
    private dataService: ServerService
  ) { }
  updateData() {
    this.dataService.toggleVars(this.binSzValue, this.varSzValue).subscribe((v: any) => {

    })
  }
  binSzMin: number = 20;
  binSzMax: number = 500;
  binSzValue: number = 100;
  varSzMin: number = 5;
  varSzMax: number = 50;
  varSzValue: number = 10;
  ngOnInit() {
  }
}
