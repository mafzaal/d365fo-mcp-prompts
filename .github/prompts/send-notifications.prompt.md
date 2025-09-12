---
mode: agent
---

## D365FO Notification Prompt Template

Send a system notification to a specific user or all users. Include:
- Title
- Message (can include emojis or links)
- Notification type (Alert, ApplicationNotification, WhatsNew, etc.)
- Severity (Informational, Warning, Error)
- Reminder interval (in seconds)
- Expiration date (ISO format)
### Example Prompt

- Type: [Alert | ApplicationNotification | WhatsNew]
- Severity: [Informational | Warning | Error]
- ReminderInterval: [seconds]
- ExpirationDateTime: [YYYY-MM-DDTHH:MM:SSZ]
- SystemNotification (entity set: SystemNotifications)
- SystemNotificationUser (entity set: SystemNotificationUsers)
- Create system notification: Use the entity set name `SystemNotifications` when creating a record.
- Associate notification with user: Use the entity set name `SystemNotificationUsers` when creating a record.


### Examples

---

### Data Entities Used
- SystemNotification (entity set: SystemNotifications)
- SystemNotificationUser (entity set: SystemNotificationUsers)
- SystemUser (entity set: SystemUsers)

### Full Entity Schemas

#### SystemNotification
- RuleId: Edm.String (Key)
- SystemNotificationId: Edm.Int64
- Title: Edm.String
- ExpirationDateTime: Edm.DateTimeOffset
- ReminderInterval: Edm.Int64
- Message: Edm.String
- Type: Microsoft.Dynamics.DataEntities.SystemNotificationType (Enum)
- Severity: Microsoft.Dynamics.DataEntities.SystemNotificationSeverity (Enum)
- SequenceId: Edm.Int64
- State: Microsoft.Dynamics.DataEntities.SystemNotificationState (Enum)

#### SystemNotificationUser
- UserId: Edm.String (Key)
- Dismissed: Microsoft.Dynamics.DataEntities.NoYes (Enum)
- SystemNotificationId: Edm.Int64

#### SystemUser
- UserID: Edm.String (Key)
- WorkflowLineItemNotificationFormat: Microsoft.Dynamics.DataEntities.WorkflowLineItemNotificationFormat (Enum)
- DocumentHandlingActive: Microsoft.Dynamics.DataEntities.NoYes (Enum)
- UserInfo_defaultPartition: Edm.Boolean
- GlobalListPageLinkMode: Edm.Int32
- GlobalExcelExportMode: Edm.Int32
- ShowAttachmentStatus: Microsoft.Dynamics.DataEntities.NoYes (Enum)
- EventPopUpLinkDestination: Microsoft.Dynamics.DataEntities.EventPopUpLinkDestination (Enum)
- NetworkDomain: Edm.String
- Company: Edm.String
- SqmGUID: Edm.Guid
- SendNotificationsInEmail: Microsoft.Dynamics.DataEntities.NoYes (Enum)
- Alias: Edm.String
- EmailProviderID: Edm.String
- Email: Edm.String
- Density: Microsoft.Dynamics.DataEntities.SysUserInfoDensity (Enum)
- DefaultCountryRegion: Edm.String
- PersonName: Edm.String
- SendAlertAsEmailMessage: Microsoft.Dynamics.DataEntities.EventEmailSendDefineMode (Enum)
- SqmEnabled: Microsoft.Dynamics.DataEntities.SysSqmEnabledClient (Enum)
- GlobalExcelExportFilePath: Edm.String
- Language: Edm.String
- EventPopUpDisplayWhen: Microsoft.Dynamics.DataEntities.EventPopupShowDefineMode (Enum)
- EventWorkflowTasksInActionCenter: Microsoft.Dynamics.DataEntities.NoYes (Enum)
- EventPollFrequency: Edm.Int32
- EventWorkflowShowPopup: Microsoft.Dynamics.DataEntities.NoYes (Enum)
- StartPage: Edm.String
- PreferredTimeZone: Microsoft.Dynamics.DataEntities.Timezone (Enum)
- HomePageRefreshDuration: Edm.Int32
- UserInfo_language: Edm.String
- Theme: Microsoft.Dynamics.DataEntities.SysUserInfoTheme (Enum)
- AutoLogOff: Edm.Int32
- MarkEmptyLinks: Microsoft.Dynamics.DataEntities.NoYes (Enum)
- Enabled: Edm.Boolean
- ShowNotificationsInTheMicrosoftDynamicsAX7Client: Microsoft.Dynamics.DataEntities.NoYes (Enum)
- Helplanguage: Edm.String
- UserName: Edm.String
- EventPopUps: Microsoft.Dynamics.DataEntities.NoYes (Enum)
- AccountType: Microsoft.Dynamics.DataEntities.UserAccountType (Enum)
- PreferredCalendar: Microsoft.Dynamics.DataEntities.PreferredCalendar (Enum)
- PreferredLocale: Edm.String
- ExternalUser: Edm.Boolean
- AutomaticUrlUpdate: Microsoft.Dynamics.DataEntities.NoYes (Enum)

### Enum Members

#### SystemNotificationType
- Alert (1): Alert
- Watchdog (2): Watchdog
- ApplicationNotification (3): Application notification
- WhatsNew (4): Whats New notification

#### SystemNotificationSeverity
- Informational (0): Informational
- Warning (1): Warning
- Error (2): Error

#### SystemNotificationState
- Active (0): Active
- Completed (1): Completed
- Expired (2): Expired
