# models/base_model.py
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

base = declarative_base()


class BaseModel(base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 👇 AGREGAR ESTA PROPIEDAD - id_key es un alias de id
    @property
    def id_key(self):
        """Alias para mantener compatibilidad con código legacy"""
        return self.id
    
    @id_key.setter
    def id_key(self, value):
        """Permite asignar id_key (lo asigna a id)"""
        self.id = value