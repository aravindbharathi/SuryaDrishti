import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { burstRow } from 'src/app/report/report.component';

@Component({
  selector: 'app-burst-table',
  templateUrl: './burst-table.component.html',
  styleUrls: ['./burst-table.component.scss']
})
export class BurstTableComponent implements OnInit {
  @Input('bursts') bursts!:Partial<burstRow>[]
  @Input('areDeleted') areDeleted!:boolean;
  // @Output('removeBurst') removeBurst:EventEmitter<number> = new EventEmitter()
  // @Output('addBurst') addBurst:EventEmitter<number> = new EventEmitter()
  @Output('rejectedBurstsChange') rejectedBurstsChange = new EventEmitter<number[]>()
  @Input('burstListEditable') burstListEditable!:boolean;
  @Input('rejectedBursts') rejectedBursts!:number[]
  displayedColumnsMain:string[]= ['peak_time','meta','chartNS','chartLM'];
  // rejectedBursts:number[] = []
  formatSeconds(totalSeconds:number){
    let pad:Function = (x:number)=>(x.toString().length==2?x.toString():'0'+x.toString())
    let hours = Math.floor(totalSeconds / 3600);
    totalSeconds %= 3600;
    let minutes = Math.floor(totalSeconds / 60);
    let seconds = totalSeconds % 60;
    return `${pad(hours)}hr ${pad(minutes)}min ${pad(seconds)}s`
  }
  filterAccepted(data:Partial<burstRow>[]){
    return data.filter((v,i,[])=>!this.rejectedBursts.includes(i));
  }
  filterRejected(data:Partial<burstRow>[]){
    return data.filter((v,i,[])=>this.rejectedBursts.includes(i))
  }
  remove(i:number){
    this.rejectedBursts.push(i)
    // this.removeBurst.emit(i)
  }
  add(i:number){
    this.rejectedBursts.splice(this.rejectedBursts.indexOf(i),1)
    // this.addBurst.emit(i)
  }
  constructor() { }

  ngOnInit(): void {
  }

}
