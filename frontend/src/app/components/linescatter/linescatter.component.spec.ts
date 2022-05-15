import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LinescatterComponent } from './linescatter.component';

describe('LinescatterComponent', () => {
  let component: LinescatterComponent;
  let fixture: ComponentFixture<LinescatterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ LinescatterComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(LinescatterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
