from voxcore.security.vault import CredentialVault
from voxcore.security.models import StoredCredential
import uuid

class CredentialService:
    def store(self, db, tenant_id, user_id, connector_type, config):
        encrypted = CredentialVault.encrypt(config)
        record = StoredCredential(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            user_id=user_id,
            connector_type=connector_type,
            encrypted_config=encrypted
        )
        db.add(record)
        db.commit()
        return record.id

    def retrieve(self, db, credential_id, tenant_id):
        record = db.query(StoredCredential).filter_by(id=credential_id, tenant_id=tenant_id).first()
        if not record:
            raise Exception("Credential not found or unauthorized")
        return CredentialVault.decrypt(record.encrypted_config)
