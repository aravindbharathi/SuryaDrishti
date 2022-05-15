import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { UploadComponent } from './upload/upload.component';
import { ReportComponent } from './report/report.component';

// Specifies the route-component mapping
const routes: Routes = [
  { path: 'upload', component: UploadComponent },
  { path: 'report/:binsize', component: ReportComponent },
  { path: '**', redirectTo: 'upload' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
