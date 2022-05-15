import { Component, Input, OnInit, ViewChild } from "@angular/core";

import {
  ChartComponent,
  ApexAxisChartSeries,
  ApexChart,
  ApexFill,
  ApexTooltip,
  ApexXAxis,
  ApexLegend,
  ApexDataLabels,
  ApexTitleSubtitle,
  ApexYAxis,
  ApexMarkers,
  ApexStroke
} from "ng-apexcharts";
import { burstRow, point, statModelData, totalData } from "src/app/report/report.component";

export type ChartOptions = {
  series: ApexAxisChartSeries;
  chart: ApexChart;
  xaxis: ApexXAxis;
  markers: ApexMarkers;
  stroke: ApexStroke;
  yaxis: ApexYAxis | ApexYAxis[];
  dataLabels: ApexDataLabels;
  title: ApexTitleSubtitle;
  legend: ApexLegend;
  fill: ApexFill;
  tooltip: ApexTooltip;
};

@Component({
  selector: "app-linescatter",
  templateUrl: "./linescatter.component.html",
  styleUrls: ["./linescatter.component.scss"]
})
export class LinescatterComponent implements OnInit {
  title = "CodeSandbox";
  // @Input('scatterData') scatterData!:any[]
  // pscatterData!:any[]
  // @Input('lineData') lineData!:any[]
  @Input() bursts!: Partial<burstRow>[];
  @Input('innerWidth') innerWidth!: number;
  @Input('statData') statData!: statModelData;
  @Input() totalData!: totalData;
  @Input() mode!: number;
  @Input() series!: ApexAxisChartSeries
  @Input('ptscatterData') ptscatterData!: point[];
  @ViewChild("chart") chart!: ChartComponent;
  @Input() tickAmt: number | undefined = 20;
  public chartOptions!: Partial<ChartOptions>;
  @Input('ptlineData') ptlineData!: point[]
  @Input() chartHeight!: number;
  lineData(totalData: totalData) {
    if (totalData) {
      return totalData.lc_data;
    }
    return []
  }
  scatterData(bursts: Partial<burstRow>[]) {
    if (bursts) {
      return this.bursts.filter(burst => [
        burst.ns?.is_detected,
        burst.lm?.is_detected,
        burst.ns?.is_detected && burst.lm?.is_detected,
        burst.ns?.is_detected || burst.lm?.is_detected,
      ][this.mode]).map(burst => {
        return {
          x: burst.peak_time,
          y: burst.peak_rate
        }
      }
      )
      // return bursts.map();
    }
    return []
  }
  constructor() { }
  ngOnInit() {



    this.chartOptions = {
      series: this.series,
      chart: {
        height: 350,
        type: "line",
        stacked: false,
        width: this.innerWidth !== null ? 0.9 * this.innerWidth : 600
        // zoom:{
        //   enabled:true,
        // },
        // toolbar:{
        //   autoSelected:,
        //   tools:{
        //     // pan:true,
        //     download:true,
        //     reset:true
        //   }
        // }
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        width: [5, 5]
      },
      title: {
        text: "Processed Light curve and Flares detected",
        align: "center",
        offsetX: 110
      },
      yaxis: [
        {
          axisTicks: {
            show: true
          },
          axisBorder: {
            show: true,
            color: "#008FFB"
          },
          labels: {
            style: {
              colors: "#008FFB"
            }
          },
          title: {
            text: "Photon count rate",
            style: {
              color: "#000000"
            }
          },
          tooltip: {
            enabled: true
          }
        }
      ],
      markers: {
        size: [8, 0]
      },
      xaxis: {
        tickAmount: 30,
        title: {
          text: "Time (s)",
          style: {
            color: "#000000"
          }
        }
      }
    };
  }


}
