import React from 'react';
import { MessageSquare, GitBranch, Clock, Trash2, Download, MoreVertical } from 'lucide-react';
import { Button } from './ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';

const ProjectsTable = ({ 
  conversations, 
  onSelectConversation,
  onDeleteConversation,
  onForkConversation,
  onExportConversation,
  currentConversationId
}) => {
  const formatDate = (date) => {
    return new Date(date).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="bg-gray-50">
            <TableHead className="w-12"></TableHead>
            <TableHead className="font-semibold">Conversación</TableHead>
            <TableHead className="font-semibold">Modelo</TableHead>
            <TableHead className="font-semibold">Mensajes</TableHead>
            <TableHead className="font-semibold">Última actualización</TableHead>
            <TableHead className="w-12"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {conversations.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="text-center py-12 text-gray-500">
                <MessageSquare className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>No hay conversaciones aún</p>
                <p className="text-sm mt-1">Crea una nueva conversación para comenzar</p>
              </TableCell>
            </TableRow>
          ) : (
            conversations.map((conv) => (
              <TableRow
                key={conv.conversation_id}
                className={`cursor-pointer hover:bg-gray-50 transition-colors ${
                  currentConversationId === conv.conversation_id ? 'bg-purple-50' : ''
                }`}
                onClick={() => onSelectConversation(conv.conversation_id)}
              >
                <TableCell>
                  <div className={`w-3 h-3 rounded-full ${
                    currentConversationId === conv.conversation_id 
                      ? 'bg-purple-600' 
                      : 'bg-gray-300'
                  }`} />
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <MessageSquare size={16} className="text-purple-600" />
                    <span className="font-medium text-gray-900">{conv.title}</span>
                    {conv.forked_from && (
                      <GitBranch size={14} className="text-purple-400" />
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                    {conv.model || 'gpt-4o'}
                  </span>
                </TableCell>
                <TableCell className="text-gray-600">
                  {conv.message_count || 0} mensajes
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Clock size={14} />
                    {formatDate(conv.updated_at)}
                  </div>
                </TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                        <MoreVertical size={16} />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={(e) => {
                        e.stopPropagation();
                        onForkConversation(conv.conversation_id);
                      }}>
                        <GitBranch className="mr-2 h-4 w-4" />
                        Bifurcar
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={(e) => {
                        e.stopPropagation();
                        onExportConversation(conv.conversation_id);
                      }}>
                        <Download className="mr-2 h-4 w-4" />
                        Exportar
                      </DropdownMenuItem>
                      <DropdownMenuItem 
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteConversation(conv.conversation_id);
                        }}
                        className="text-red-600"
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Eliminar
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
};

export default ProjectsTable;
