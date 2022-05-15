import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BurstTableComponent } from './burst-table.component';

describe('BurstTableComponent', () => {
  let component: BurstTableComponent;
  let fixture: ComponentFixture<BurstTableComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BurstTableComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(BurstTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
