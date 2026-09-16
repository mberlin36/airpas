import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SubmissionList } from './submission-list';

describe('SubmissionList', () => {
  let component: SubmissionList;
  let fixture: ComponentFixture<SubmissionList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SubmissionList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SubmissionList);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
