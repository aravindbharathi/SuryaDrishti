import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatChipsModule } from '@angular/material/chips';

// Components
import { AppComponent } from './app.component';
import { UploadComponent } from './upload/upload.component';
import { DialogOptionsDialog, ReportComponent } from './report/report.component';

// Material Modules
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSliderModule } from '@angular/material/slider';
import { MatButtonToggleModule } from '@angular/material/button-toggle'
import { MatGridListModule } from '@angular/material/grid-list';
// Addons
import { NgApexchartsModule } from 'ng-apexcharts';
import { MatDialogModule } from '@angular/material/dialog';
import { LinescatterComponent } from './components/linescatter/linescatter.component';
import { BurstTableComponent } from './components/burst-table/burst-table.component';
import { MatSelectModule } from '@angular/material/select';
import { LinechartComponent } from './components/linechart/linechart.component';


@NgModule({
  declarations: [
    AppComponent,
    UploadComponent,
    ReportComponent,
    DialogOptionsDialog,
    LinescatterComponent,
    BurstTableComponent,
    LinechartComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    MatProgressBarModule,
    ReactiveFormsModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    MatSnackBarModule,
    MatGridListModule,
    MatSliderModule,
    MatSelectModule,
    MatButtonToggleModule,
    MatCardModule,
    MatFormFieldModule,
    MatToolbarModule,
    MatDialogModule,
    MatButtonModule,
    MatChipsModule,
    MatTableModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatExpansionModule,
    NgApexchartsModule,
    FormsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
