import { Component, ElementRef, HostListener, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { UploadComponent } from './upload/upload.component';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'frontend';
  url = '';
  constructor(public route:ActivatedRoute){

  }
  ngOnInit(): void {
    this.url = window.location.href;
  }
  toUpload(force:boolean){
    if(force){
      localStorage.setItem('allowUnload','true');
    }
    else{
      localStorage.setItem('allowUnload','false');
    }
    window.location.href= '/upload'
  }

}
