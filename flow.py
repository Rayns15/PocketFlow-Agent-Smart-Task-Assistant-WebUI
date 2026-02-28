from pocketflow import Flow
from nodes import (
    InputTaskNode, ValidationNode, CategorizeNode, 
    ProcessNode, SaveNode, SummaryNode, UpdateTaskNode,
    CheckDeadlinesNode, DeleteTaskNode, ChangeStatusNode, 
    ReorderTasksNode, EditTaskDetailsNode
)

input_n = InputTaskNode()
valid_n = ValidationNode()
logic_n = CategorizeNode()
work_n = ProcessNode()
save_n = SaveNode() 
report_n = SummaryNode()
update_n = UpdateTaskNode()
check_n = CheckDeadlinesNode() 
delete_n = DeleteTaskNode()
status_n = ChangeStatusNode() 
reorder_n = ReorderTasksNode()
edit_n = EditTaskDetailsNode()

# Input Branching
input_n - "create" >> valid_n
input_n - "done" >> update_n
input_n - "delete" >> delete_n   
input_n - "view" >> report_n
input_n - "status" >> status_n
input_n - "edit" >> edit_n

# Standard Creation Graph
valid_n - "valid" >> logic_n
logic_n - "high_priority" >> work_n
logic_n - "low_priority" >> work_n
input_n - "reorder" >> reorder_n 

# Converge on Save (Now includes edit_n)
work_n >> save_n       
update_n >> save_n     
delete_n >> save_n     
status_n >> save_n   
reorder_n >> save_n   
edit_n >> save_n 

# End Flow
save_n >> report_n     
report_n >> check_n    

task_flow = Flow(input_n)