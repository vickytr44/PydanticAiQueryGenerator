full_schema = """
schema {
  query: Query
}
type Account {
  id: Int!
  number: String!
  isActive: Boolean!
  type: AccountType!
  customerId: Int!
  customer: Customer!
  bills(where: BillFilterInput  order: [BillSortInput!] ): [Bill!]!
}
type AccountsConnection {
  pageInfo: PageInfo!
  edges: [AccountsEdge!]
  nodes: [Account!]
  totalCount: Int! 
}
type AccountsEdge {
  cursor: String!
  node: Account!
}
type AvailableEntity {
  id: String!
  value: String!
}
type AvailableField {
  name: String!
  type: String!
}
type AvailableOperator {
  name: String!
}
type Bill {
  id: Int!
  number: Int!
  month: Month!
  isActive: Boolean!
  status: Status!
  dueDate: Date!
  amount: Decimal!
  customerId: Int!
  customer: Customer!
  accountId: Int!
  account: Account!
}
type BillsConnection {
  pageInfo: PageInfo!
  edges: [BillsEdge!]
  nodes: [Bill!]
  totalCount: Int! 
}
type BillsEdge {
  cursor: String!
  node: Bill!
}
type Customer {
  id: Int!
  name: String!
  identityNumber: Int!
  age: Int!
  accounts(where: AccountFilterInput  order: [AccountSortInput!] ): [Account!]!
  bills(where: BillFilterInput  order: [BillSortInput!] ): [Bill!]!
}
type CustomersConnection {
  pageInfo: PageInfo!
  edges: [CustomersEdge!]
  nodes: [Customer!]
  totalCount: Int! 
}
type CustomersEdge {
  cursor: String!
  node: Customer!
}
type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
type Query {
  accounts( first: Int  after: String  last: Int  before: String where: AccountFilterInput  order: [AccountSortInput!] ): AccountsConnection  
  availableEntities(where: AvailableEntityFilterInput  order: [AvailableEntitySortInput!] ): [AvailableEntity!]!
  availableRelatedEntities(entity: String! where: AvailableEntityFilterInput  order: [AvailableEntitySortInput!] ): [AvailableEntity!]!
  availableFields(entity: String! where: AvailableFieldFilterInput  order: [AvailableFieldSortInput!] ): [AvailableField!]!
  availableOperators(entity: String! field: String! where: AvailableOperatorFilterInput  order: [AvailableOperatorSortInput!] ): [AvailableOperator!]!
  bills( first: Int  after: String  last: Int  before: String where: BillFilterInput  order: [BillSortInput!] ): BillsConnection  
  customers( first: Int  after: String  last: Int  before: String where: CustomerFilterInput  order: [CustomerSortInput!] ): CustomersConnection  
  cleanedSchema(schemaName: Entity!): String!
}
input AccountFilterInput {
  and: [AccountFilterInput!]
  or: [AccountFilterInput!]
  id: IntOperationFilterInput
  number: StringOperationFilterInput
  isActive: BooleanOperationFilterInput
  type: AccountTypeOperationFilterInput
  customerId: IntOperationFilterInput
  customer: CustomerFilterInput
  bills: ListFilterInputTypeOfBillFilterInput
}
input AccountSortInput {
  id: SortEnumType 
  number: SortEnumType 
  isActive: SortEnumType 
  type: SortEnumType 
  customerId: SortEnumType 
  customer: CustomerSortInput 
}
input AccountTypeOperationFilterInput {
  eq: AccountType 
  neq: AccountType 
  in: [AccountType!] 
  nin: [AccountType!] 
}
input AvailableEntityFilterInput {
  and: [AvailableEntityFilterInput!]
  or: [AvailableEntityFilterInput!]
  id: StringOperationFilterInput
  value: StringOperationFilterInput
}
input AvailableEntitySortInput {
  id: SortEnumType 
  value: SortEnumType 
}
input AvailableFieldFilterInput {
  and: [AvailableFieldFilterInput!]
  or: [AvailableFieldFilterInput!]
  name: StringOperationFilterInput
  type: StringOperationFilterInput
}
input AvailableFieldSortInput {
  name: SortEnumType 
  type: SortEnumType 
}
input AvailableOperatorFilterInput {
  and: [AvailableOperatorFilterInput!]
  or: [AvailableOperatorFilterInput!]
  name: StringOperationFilterInput
}
input AvailableOperatorSortInput {
  name: SortEnumType 
}
input BillFilterInput {
  and: [BillFilterInput!]
  or: [BillFilterInput!]
  id: IntOperationFilterInput
  number: IntOperationFilterInput
  month: MonthOperationFilterInput
  isActive: BooleanOperationFilterInput
  status: StatusOperationFilterInput
  dueDate: DateOperationFilterInput
  amount: DecimalOperationFilterInput
  customerId: IntOperationFilterInput
  customer: CustomerFilterInput
  accountId: IntOperationFilterInput
  account: AccountFilterInput
}
input BillSortInput {
  id: SortEnumType 
  number: SortEnumType 
  month: SortEnumType 
  isActive: SortEnumType 
  status: SortEnumType 
  dueDate: SortEnumType 
  amount: SortEnumType 
  customerId: SortEnumType 
  customer: CustomerSortInput 
  accountId: SortEnumType 
  account: AccountSortInput 
}
input BooleanOperationFilterInput {
  eq: Boolean 
  neq: Boolean 
}
input CustomerFilterInput {
  and: [CustomerFilterInput!]
  or: [CustomerFilterInput!]
  id: IntOperationFilterInput
  name: StringOperationFilterInput
  identityNumber: IntOperationFilterInput
  age: IntOperationFilterInput
  accounts: ListFilterInputTypeOfAccountFilterInput
  bills: ListFilterInputTypeOfBillFilterInput
}
input CustomerSortInput {
  id: SortEnumType 
  name: SortEnumType 
  identityNumber: SortEnumType 
  age: SortEnumType 
}
input DateOperationFilterInput {
  eq: Date 
  neq: Date 
  in: [Date] 
  nin: [Date] 
  gt: Date 
  ngt: Date 
  gte: Date 
  ngte: Date 
  lt: Date 
  nlt: Date 
  lte: Date 
  nlte: Date 
}
input DecimalOperationFilterInput {
  eq: Decimal 
  neq: Decimal 
  in: [Decimal] 
  nin: [Decimal] 
  gt: Decimal 
  ngt: Decimal 
  gte: Decimal 
  ngte: Decimal 
  lt: Decimal 
  nlt: Decimal 
  lte: Decimal 
  nlte: Decimal 
}
input IntOperationFilterInput {
  eq: Int 
  neq: Int 
  in: [Int] 
  nin: [Int] 
  gt: Int 
  ngt: Int 
  gte: Int 
  ngte: Int 
  lt: Int 
  nlt: Int 
  lte: Int 
  nlte: Int 
}
input ListFilterInputTypeOfAccountFilterInput {
  all: AccountFilterInput 
  none: AccountFilterInput 
  some: AccountFilterInput 
  any: Boolean 
}
input ListFilterInputTypeOfBillFilterInput {
  all: BillFilterInput 
  none: BillFilterInput 
  some: BillFilterInput 
  any: Boolean 
}
input MonthOperationFilterInput {
  eq: Month 
  neq: Month 
  in: [Month!] 
  nin: [Month!] 
}
input StatusOperationFilterInput {
  eq: Status 
  neq: Status 
  in: [Status!] 
  nin: [Status!] 
}
input StringOperationFilterInput {
  and: [StringOperationFilterInput!]
  or: [StringOperationFilterInput!]
  eq: String 
  neq: String 
  contains: String 
  ncontains: String 
  in: [String] 
  nin: [String] 
  startsWith: String 
  nstartsWith: String 
  endsWith: String 
  nendsWith: String 
}
enum AccountType {
  DOMESTIC
  COMMERCIAL
}
enum Entity {
  ACCOUNT
  CUSTOMER
  BILL
}
enum Month {
  JANUARY
  FEBRUARY
  MARCH
  APRIL
  MAY
  JUNE
  JULY
  AUGUST
  SEPTEMBER
  OCTOBER
  NOVEMBER
  DECEMBER
}
enum SortEnumType {
  ASC
  DESC
}
enum Status {
  PAID
  NOT_PAID
}
scalar Date
scalar Decimal
"""