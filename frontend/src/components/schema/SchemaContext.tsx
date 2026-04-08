import React, { createContext, useContext, useState } from "react";

const SchemaContext = createContext(null);

export const SchemaProvider = ({ children }) => {
  const [activeConnectionId, setActiveConnectionId] = useState(null);
  const [schema, setSchema] = useState(null);

  return (
    <SchemaContext.Provider
      value={{
        activeConnectionId,
        setActiveConnectionId,
        schema,
        setSchema,
      }}
    >
      {children}
    </SchemaContext.Provider>
  );
};

export const useSchema = () => useContext(SchemaContext);

export default SchemaContext;
