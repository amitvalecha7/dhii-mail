/**
 * Frontend Protocol Types for Enterprise-Scale UI
 * Defines the JSON protocol between Python Backend and React Frontend
 */

// Orchestrator Output Envelope (from backend)
export interface OrchestratorOutput {
  request_id: string;
  tenant_id: string;
  user_id: string;
  state: 'STREAMING' | 'WAITING_FOR_CONFIRMATION' | 'COMPLETED' | 'ERROR';
  explanation?: string;
  chunks: UIChunk[];
  timestamp: string;
}

// UI Chunk Types (New Design Spec v1.2)
export type UIChunk = 
  | TextBlockChunk
  | AggregatedCardChunk
  | DataTableChunk
  | ListCardChunk
  | ActionCardChunk
  | FormCardChunk
  | ErrorCardChunk;

export interface BaseChunk {
  type: string;
}

export interface TextBlockChunk extends BaseChunk {
  type: 'TextBlock';
  content: string;
  tone: 'neutral' | 'advisory' | 'warning';
  collapsible: boolean;
  completed: boolean;
}

export interface AggregatedCardChunk extends BaseChunk {
  type: 'AggregatedCard';
  title: string;
  sources: string[];
  items: Array<{
    label: string;
    value: number | string;
  }>;
  multiple_sources: boolean;
  partial_rendering: boolean;
  importance_based_layout: boolean;
}

export interface DataTableChunk extends BaseChunk {
  type: 'DataTable';
  headers: string[];
  rows: any[][];
  sortable?: boolean;
  filterable?: boolean;
}

export interface ListCardChunk extends BaseChunk {
  type: 'ListCard';
  title: string;
  items: Array<{
    id: string;
    title: string;
    subtitle?: string;
    icon?: string;
    actions?: Action[];
  }>;
}

export interface ActionCardChunk extends BaseChunk {
  type: 'ActionCard';
  title: string;
  description: string;
  actions: Action[];
  priority?: 'low' | 'medium' | 'high';
}

export interface FormCardChunk extends BaseChunk {
  type: 'FormCard';
  title: string;
  fields: FormField[];
  submit_action: Action;
}

export interface ErrorCardChunk extends BaseChunk {
  type: 'ErrorCard';
  title: string;
  message: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  actions?: Action[];
}

// Common Types
export interface Action {
  id: string;
  label: string;
  type: 'button' | 'link' | 'submit';
  variant?: 'primary' | 'secondary' | 'danger';
  disabled?: boolean;
  payload?: any;
}

export interface FormField {
  id: string;
  type: 'text' | 'email' | 'password' | 'textarea' | 'select' | 'checkbox';
  label: string;
  placeholder?: string;
  required?: boolean;
  options?: Array<{ value: string; label: string }>;
  validation?: ValidationRule[];
}

export interface ValidationRule {
  type: 'required' | 'email' | 'minLength' | 'maxLength' | 'pattern';
  value?: any;
  message: string;
}

// Adjacency List for ComponentGraph
export interface AdjacencyList {
  nodes: Record<string, ComponentNode>;
  rootId: string;
  operations: AdjacencyOperation[];
}

export interface ComponentNode {
  id: string;
  type: string;
  props: Record<string, any>;
  children: string[];
}

export interface AdjacencyOperation {
  operation: 'insert' | 'update' | 'delete';
  nodeId: string;
  parentId?: string;
  position?: number;
}