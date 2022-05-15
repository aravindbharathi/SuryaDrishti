import { Component, Input, OnInit, ViewChild } from "@angular/core";

import {
  ChartComponent,
  ApexAxisChartSeries,
  ApexChart,
  ApexYAxis,
  ApexXAxis,
} from "ng-apexcharts";
import { point } from "src/app/report/report.component";

export type ChartOptions = {
  series: ApexAxisChartSeries;
  chart: ApexChart;
  xaxis: ApexXAxis;
  yaxis: ApexYAxis;
};

@Component({
  selector: "app-linechart",
  templateUrl: "./linechart.component.html",
  styleUrls: ["./linechart.component.scss"]
})
export class LinechartComponent implements OnInit {
  @ViewChild("chart") chart!: ChartComponent;
  @Input() innerWidth!:number;
  @Input() series!:ApexAxisChartSeries
  public chartOptions!: Partial<ChartOptions>;

  constructor() {
  }
  ngOnInit() {
    this.chartOptions = {
      series: this.series,
      chart: {  
        height:300,
        width:this.innerWidth!==null?(0.9*this.innerWidth):600,
        type: 'scatter',
        zoom: {
          enabled: true,
          type: 'xy'
        },
        animations:{
          enabled:false
        }
      },
      xaxis:{
        tickAmount:30
      }
    };
  }
}
