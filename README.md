# Wood plank quality control system
## On AI vision based wood plank quality control system, with AI model training, defect detection, Siemens PLC Simulation (using S7 protocol) and statistic webpage that works in real time.

### Default PLC server port is set to 1102.

## PLC Interface Map (DB1 - Commands)

| Offset | Name     | Type | Who writes | Description               |
|--------|----------|------|------------|---------------------------|
| 0      | cmd_code | INT  | Client     | 0=nothing, 1=PASS, 2=DROP |
| 2      | part_id  | INT  | Client     | Detail number             |
| 4.0 | new_cmd | BOOL | Client | Set to 1 when command is ready, PLC resets to 0 |

## PLC Interface Map (DB2 - Status)

| Offset | Name | Type | Who writes | Description |
|--------|------|------|------------|-------------|
| 0 | heartbeat | INT | PLC | Increments every cycle, shows that simulator is alive |
| 2 | line_state | INT | PLC | 0=stopped, 1=working, 2=error, 3=E-stop |
| 4.0 | cmd_ack | BOOL | PLC | Command accepted |
| 4.1 | part_at_inspection | BOOL | PLC | Detail is in inspection place |
| 4.2 | part_at_gate | BOOL | PLC | Detail is next to the pushing gates |
| 4.3 | pusher_active | BOOL | PLC | Pusher is currently active |
| 6 | waiting_part_id | INT | PLC | Detail that waits for result (0=no one) |
| 8 | last_part_id | INT | PLC | Last processed detail |
| 10 | last_result | INT | PLC | 1=skipped, 2=pushed, 3=missed |
| 12 | count_passed | DINT | PLC | Skipped detail count |
| 16 | count_dropped | DINT | PLC | Pushed detail count |
| 20 | fault_code | INT | PLC | 0=nothing, 1=command late, 2=unknown detail, 3=pushing failed, 4=unknown command |