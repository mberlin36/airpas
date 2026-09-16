import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TaskTable } from './task-table';

describe('TaskTable', () => {
  let component: TaskTable;
  let fixture: ComponentFixture<TaskTable>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TaskTable]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TaskTable);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
