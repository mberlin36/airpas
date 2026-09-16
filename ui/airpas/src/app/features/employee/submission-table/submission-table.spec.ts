import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SubmissionTable } from './submission-table';

describe('SubmissionTable', () => {
  let component: SubmissionTable;
  let fixture: ComponentFixture<SubmissionTable>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SubmissionTable]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SubmissionTable);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
