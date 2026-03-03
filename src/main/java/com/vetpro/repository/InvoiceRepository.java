package com.vetpro.repository;

import com.vetpro.model.Invoice;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface InvoiceRepository extends JpaRepository<Invoice, Long> {

    List<Invoice> findByOwnerId(Long ownerId);

    List<Invoice> findByPaidFalse();
}
