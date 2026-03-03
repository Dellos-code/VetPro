package com.vetpro.repository;

import com.vetpro.model.Appointment;
import com.vetpro.model.AppointmentStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface AppointmentRepository extends JpaRepository<Appointment, Long> {

    List<Appointment> findByPetId(Long petId);

    List<Appointment> findByVeterinarianId(Long vetId);

    List<Appointment> findByStatus(AppointmentStatus status);

    List<Appointment> findByDateTimeBetween(LocalDateTime start, LocalDateTime end);
}
