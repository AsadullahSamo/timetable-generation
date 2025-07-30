import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { CheckCircle, XCircle, AlertTriangle, RefreshCw, Search, Wrench } from 'lucide-react';

const ConstraintManager = () => {
  const [validationResult, setValidationResult] = useState(null);
  const [resolutionResult, setResolutionResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeOperation, setActiveOperation] = useState(null);

  const validateConstraints = async () => {
    setLoading(true);
    setActiveOperation('validate');
    
    try {
      const response = await fetch('/api/timetable/validate-constraints/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      
      if (data.success) {
        setValidationResult(data.validation_result);
      } else {
        console.error('Validation failed:', data.error);
      }
    } catch (error) {
      console.error('Error validating constraints:', error);
    } finally {
      setLoading(false);
      setActiveOperation(null);
    }
  };

  const resolveConstraints = async () => {
    setLoading(true);
    setActiveOperation('resolve');
    
    try {
      const response = await fetch('/api/timetable/resolve-constraints/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      setResolutionResult(data);
      
      // After resolution, re-validate to show updated status
      if (data.success) {
        setTimeout(() => {
          validateConstraints();
        }, 1000);
      }
    } catch (error) {
      console.error('Error resolving constraints:', error);
    } finally {
      setLoading(false);
      setActiveOperation(null);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'PASS':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'FAIL':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'HIGH':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'LOW':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="w-5 h-5" />
            Constraint Validation & Resolution System
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <Button
              onClick={validateConstraints}
              disabled={loading}
              variant="outline"
              className="flex items-center gap-2"
            >
              {loading && activeOperation === 'validate' ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}
              Check Constraints
            </Button>
            
            <Button
              onClick={resolveConstraints}
              disabled={loading || !validationResult || validationResult.overall_compliance}
              className="flex items-center gap-2"
            >
              {loading && activeOperation === 'resolve' ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Wrench className="w-4 h-4" />
              )}
              Fix Violations
            </Button>
          </div>
          
          <p className="text-sm text-gray-600 mt-2">
            Use "Check Constraints" to validate all scheduling rules, then "Fix Violations" to automatically resolve issues.
          </p>
        </CardContent>
      </Card>

      {/* Validation Results */}
      {validationResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {validationResult.overall_compliance ? (
                <CheckCircle className="w-5 h-5 text-green-500" />
              ) : (
                <XCircle className="w-5 h-5 text-red-500" />
              )}
              Constraint Validation Results
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Summary */}
              <Alert className={validationResult.overall_compliance ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
                <AlertDescription>
                  <div className="flex items-center justify-between">
                    <span>
                      {validationResult.overall_compliance 
                        ? '🎉 All constraints satisfied!' 
                        : `❌ ${validationResult.total_violations} violations found`}
                    </span>
                    <Badge variant={validationResult.overall_compliance ? 'success' : 'destructive'}>
                      {validationResult.overall_compliance ? 'COMPLIANT' : 'VIOLATIONS'}
                    </Badge>
                  </div>
                </AlertDescription>
              </Alert>

              {/* Constraint Breakdown */}
              <div className="grid gap-3">
                <h4 className="font-semibold text-sm text-gray-700">Constraint Details:</h4>
                {Object.entries(validationResult.constraint_results).map(([constraintName, result]) => (
                  <div key={constraintName} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(result.status)}
                      <span className="font-medium">{constraintName}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={result.status === 'PASS' ? 'success' : 'destructive'}>
                        {result.violations} violations
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>

              {/* Detailed Violations */}
              {validationResult.total_violations > 0 && (
                <div className="space-y-3">
                  <h4 className="font-semibold text-sm text-gray-700">Top Violations:</h4>
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {Object.entries(validationResult.violations_by_constraint).map(([constraintName, violations]) => 
                      violations.slice(0, 3).map((violation, index) => (
                        <div key={`${constraintName}-${index}`} className="p-2 border-l-4 border-red-400 bg-red-50 rounded">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-red-800">{constraintName}</span>
                            {violation.severity && (
                              <Badge className={`text-xs ${getSeverityColor(violation.severity)}`}>
                                {violation.severity}
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-red-700 mt-1">{violation.description}</p>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Resolution Results */}
      {resolutionResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Wrench className="w-5 h-5" />
              Constraint Resolution Results
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Alert className={resolutionResult.success ? 'border-green-200 bg-green-50' : 'border-yellow-200 bg-yellow-50'}>
              <AlertDescription>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">
                      {resolutionResult.success ? '✅ Resolution Successful' : '⚠️ Partial Resolution'}
                    </span>
                    <Badge variant={resolutionResult.success ? 'success' : 'warning'}>
                      {resolutionResult.resolution_result?.iterations || 0} iterations
                    </Badge>
                  </div>
                  <p className="text-sm">{resolutionResult.message}</p>
                  
                  {resolutionResult.resolution_result && (
                    <div className="grid grid-cols-2 gap-4 mt-3 text-sm">
                      <div>
                        <span className="font-medium">Final Violations:</span> {resolutionResult.resolution_result.final_violations}
                      </div>
                      <div>
                        <span className="font-medium">Entries Updated:</span> {resolutionResult.resolution_result.entries_updated || 0}
                      </div>
                    </div>
                  )}
                </div>
              </AlertDescription>
            </Alert>

            {/* Resolution Log */}
            {resolutionResult.resolution_result?.resolution_log && (
              <div className="mt-4 space-y-2">
                <h4 className="font-semibold text-sm text-gray-700">Resolution Log:</h4>
                <div className="space-y-1 max-h-40 overflow-y-auto">
                  {resolutionResult.resolution_result.resolution_log.slice(0, 10).map((log, index) => (
                    <div key={index} className="text-xs p-2 bg-gray-50 rounded flex items-center justify-between">
                      <span>{log.violation}</span>
                      <Badge variant={log.status === 'RESOLVED' ? 'success' : 'destructive'} className="text-xs">
                        {log.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ConstraintManager;
