/**
 * Deterministic Renderer for New Design Spec v1.2
 * Stateless, tenant-agnostic component renderer
 * Zero business logic - pure UI rendering from orchestrator output
 */

import React from 'react';
import { 
  OrchestratorOutput, 
  UIChunk, 
  TextBlockChunk, 
  AggregatedCardChunk,
  DataTableChunk,
  ListCardChunk,
  ActionCardChunk,
  FormCardChunk,
  ErrorCardChunk,
  AdjacencyList
} from '../types/protocol';

interface DeterministicRendererProps {
  orchestratorOutput: OrchestratorOutput;
  onAction?: (actionId: string, payload?: any) => void;
  onFormSubmit?: (formId: string, data: Record<string, any>) => void;
}

/**
 * Pure, deterministic renderer that converts orchestrator output to React components
 * No business logic, no data fetching, no state management
 */
export const DeterministicRenderer: React.FC<DeterministicRendererProps> = ({ 
  orchestratorOutput, 
  onAction, 
  onFormSubmit 
}) => {
  return (
    <div className="deterministic-ui-container">
      {orchestratorOutput.explanation && (
        <div className="ui-explanation text-sm text-slate-500 mb-4">
          {orchestratorOutput.explanation}
        </div>
      )}
      
      <div className="ui-chunks">
        {orchestratorOutput.chunks.map((chunk, index) => (
          <UIChunkRenderer 
            key={`${orchestratorOutput.request_id}-${index}`}
            chunk={chunk}
            onAction={onAction}
            onFormSubmit={onFormSubmit}
          />
        ))}
      </div>
    </div>
  );
};

interface UIChunkRendererProps {
  chunk: UIChunk;
  onAction?: (actionId: string, payload?: any) => void;
  onFormSubmit?: (formId: string, data: Record<string, any>) => void;
}

/**
 * Chunk-specific renderer - dispatches to appropriate component based on chunk type
 */
const UIChunkRenderer: React.FC<UIChunkRendererProps> = ({ chunk, onAction, onFormSubmit }) => {
  switch (chunk.type) {
    case 'TextBlock':
      return <TextBlockComponent chunk={chunk as TextBlockChunk} />;
    
    case 'AggregatedCard':
      return <AggregatedCardComponent chunk={chunk as AggregatedCardChunk} />;
    
    case 'DataTable':
      return <DataTableComponent chunk={chunk as DataTableChunk} />;
    
    case 'ListCard':
      return <ListCardComponent chunk={chunk as ListCardChunk} onAction={onAction} />;
    
    case 'ActionCard':
      return <ActionCardComponent chunk={chunk as ActionCardChunk} onAction={onAction} />;
    
    case 'FormCard':
      return <FormCardComponent chunk={chunk as FormCardChunk} onFormSubmit={onFormSubmit} />;
    
    case 'ErrorCard':
      return <ErrorCardComponent chunk={chunk as ErrorCardChunk} onAction={onAction} />;
    
    default:
      return <ErrorCardComponent 
        chunk={{
          type: 'ErrorCard',
          title: 'Unknown Component Type',
          message: `Unsupported chunk type: ${(chunk as any).type}`,
          severity: 'error'
        }} 
      />;
  }
};

// === STATELESS COMPONENT RENDERERS ===

interface TextBlockProps {
  chunk: TextBlockChunk;
}

const TextBlockComponent: React.FC<TextBlockProps> = ({ chunk }) => {
  const toneClasses = {
    neutral: 'text-slate-700',
    advisory: 'text-blue-600 border-l-4 border-blue-500 pl-4',
    warning: 'text-amber-600 border-l-4 border-amber-500 pl-4'
  };

  return (
    <div className={`text-block text-sm leading-relaxed mb-4 ${toneClasses[chunk.tone]}`}>
      {chunk.content}
      {chunk.collapsible && (
        <div className="text-xs text-slate-500 mt-1">
          {chunk.completed ? '✓ Completed' : '⋯ In Progress'}
        </div>
      )}
    </div>
  );
};

interface AggregatedCardProps {
  chunk: AggregatedCardChunk;
}

const AggregatedCardComponent: React.FC<AggregatedCardProps> = ({ chunk }) => {
  return (
    <div className="aggregated-card bg-white rounded-lg shadow-sm border border-slate-200 p-6 mb-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-900">{chunk.title}</h3>
        <div className="flex gap-2">
          {chunk.sources.map(source => (
            <span key={source} className="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded">
              {source}
            </span>
          ))}
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        {chunk.items.map((item, index) => (
          <div key={index} className="text-center">
            <div className="text-2xl font-bold text-slate-900">{item.value}</div>
            <div className="text-sm text-slate-600">{item.label}</div>
          </div>
        ))}
      </div>
      
      {chunk.partial_rendering && (
        <div className="mt-4 text-xs text-slate-500">
          {chunk.multiple_sources ? 'Multi-source aggregation' : 'Single source'}
          {chunk.importance_based_layout && ' • Importance ordered'}
        </div>
      )}
    </div>
  );
};

interface DataTableProps {
  chunk: DataTableChunk;
}

const DataTableComponent: React.FC<DataTableProps> = ({ chunk }) => {
  return (
    <div className="data-table overflow-x-auto mb-4">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            {chunk.headers.map((header, index) => (
              <th key={index} className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-slate-200">
          {chunk.rows.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((cell, cellIndex) => (
                <td key={cellIndex} className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

interface ListCardProps {
  chunk: ListCardChunk;
  onAction?: (actionId: string, payload?: any) => void;
}

const ListCardComponent: React.FC<ListCardProps> = ({ chunk, onAction }) => {
  return (
    <div className="list-card bg-white rounded-lg shadow-sm border border-slate-200 p-6 mb-4">
      <h3 className="text-lg font-semibold text-slate-900 mb-4">{chunk.title}</h3>
      <div className="space-y-3">
        {chunk.items.map((item) => (
          <div key={item.id} className="flex items-center justify-between p-3 hover:bg-slate-50 rounded-lg">
            <div className="flex items-center gap-3">
              {item.icon && <span className="text-slate-400">{item.icon}</span>}
              <div>
                <div className="font-medium text-slate-900">{item.title}</div>
                {item.subtitle && <div className="text-sm text-slate-600">{item.subtitle}</div>}
              </div>
            </div>
            {item.actions && (
              <div className="flex gap-2">
                {item.actions.map((action) => (
                  <button
                    key={action.id}
                    onClick={() => onAction?.(action.id, action.payload)}
                    className="text-sm px-3 py-1 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700"
                    disabled={action.disabled}
                  >
                    {action.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

interface ActionCardProps {
  chunk: ActionCardChunk;
  onAction?: (actionId: string, payload?: any) => void;
}

const ActionCardComponent: React.FC<ActionCardProps> = ({ chunk, onAction }) => {
  const priorityColors = {
    low: 'border-slate-200',
    medium: 'border-blue-200',
    high: 'border-red-200'
  };

  return (
    <div className={`action-card bg-white rounded-lg shadow-sm border ${priorityColors[chunk.priority || 'medium']} p-6 mb-4`}>
      <h3 className="text-lg font-semibold text-slate-900 mb-2">{chunk.title}</h3>
      <p className="text-slate-600 mb-4">{chunk.description}</p>
      <div className="flex gap-3">
        {chunk.actions.map((action) => (
          <button
            key={action.id}
            onClick={() => onAction?.(action.id, action.payload)}
            className={`px-4 py-2 rounded-md font-medium ${
              action.variant === 'primary' ? 'bg-blue-600 text-white hover:bg-blue-700' :
              action.variant === 'danger' ? 'bg-red-600 text-white hover:bg-red-700' :
              'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
            disabled={action.disabled}
          >
            {action.label}
          </button>
        ))}
      </div>
    </div>
  );
};

interface FormCardProps {
  chunk: FormCardChunk;
  onFormSubmit?: (formId: string, data: Record<string, any>) => void;
}

const FormCardComponent: React.FC<FormCardProps> = ({ chunk, onFormSubmit }) => {
  const [formData, setFormData] = React.useState<Record<string, any>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onFormSubmit?.(chunk.submit_action.id, formData);
  };

  return (
    <form onSubmit={handleSubmit} className="form-card bg-white rounded-lg shadow-sm border border-slate-200 p-6 mb-4">
      <h3 className="text-lg font-semibold text-slate-900 mb-4">{chunk.title}</h3>
      <div className="space-y-4">
        {chunk.fields.map((field) => (
          <div key={field.id}>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            {field.type === 'select' ? (
              <select
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={formData[field.id] || ''}
                onChange={(e) => setFormData({...formData, [field.id]: e.target.value})}
                required={field.required}
              >
                <option value="">{field.placeholder}</option>
                {field.options?.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            ) : field.type === 'textarea' ? (
              <textarea
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder={field.placeholder}
                value={formData[field.id] || ''}
                onChange={(e) => setFormData({...formData, [field.id]: e.target.value})}
                required={field.required}
              />
            ) : (
              <input
                type={field.type}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder={field.placeholder}
                value={formData[field.id] || ''}
                onChange={(e) => setFormData({...formData, [field.id]: e.target.value})}
                required={field.required}
              />
            )}
          </div>
        ))}
      </div>
      <button
        type="submit"
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
      >
        {chunk.submit_action.label}
      </button>
    </form>
  );
};

interface ErrorCardProps {
  chunk: ErrorCardChunk;
  onAction?: (actionId: string, payload?: any) => void;
}

const ErrorCardComponent: React.FC<ErrorCardProps> = ({ chunk, onAction }) => {
  const severityColors = {
    info: 'border-blue-200 bg-blue-50',
    warning: 'border-amber-200 bg-amber-50',
    error: 'border-red-200 bg-red-50',
    critical: 'border-red-300 bg-red-100'
  };

  return (
    <div className={`error-card rounded-lg border ${severityColors[chunk.severity]} p-6 mb-4`}>
      <h3 className="text-lg font-semibold text-slate-900 mb-2">{chunk.title}</h3>
      <p className="text-slate-700 mb-4">{chunk.message}</p>
      {chunk.actions && (
        <div className="flex gap-3">
          {chunk.actions.map((action) => (
            <button
              key={action.id}
              onClick={() => onAction?.(action.id, action.payload)}
              className="text-sm px-3 py-1 rounded-md bg-white hover:bg-slate-100 text-slate-700 border border-slate-300"
            >
              {action.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default DeterministicRenderer;